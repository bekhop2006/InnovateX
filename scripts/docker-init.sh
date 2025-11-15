#!/bin/bash

# InnovateX Docker Initialization Script
# This script sets up the Docker environment for the first time

set -e

echo "🚀 Initializing InnovateX Docker Environment..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    
    # Create .env file with default values
    cat > .env << EOF
# InnovateX Environment Configuration
# Auto-generated for development

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=innovatex_db
POSTGRES_PORT=5432

# Application Configuration
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
BACKEND_PORT=8000

# Security Configuration (change in production!)
SECRET_KEY=$(openssl rand -hex 32)

# CORS Configuration
CORS_ORIGINS=*

# PgAdmin Configuration
PGADMIN_EMAIL=admin@innovatex.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
EOF
    
    echo -e "${GREEN}✅ .env file created with secure SECRET_KEY${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating necessary directories...${NC}"

mkdir -p backend/uploads/avatars
mkdir -p models
mkdir -p dataset/pdfs

echo -e "${GREEN}✅ Directories created${NC}"

# Stop any existing containers
echo ""
echo -e "${BLUE}🛑 Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Build images
echo ""
echo -e "${BLUE}🏗️  Building Docker images...${NC}"
docker-compose build

# Start services
echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo ""
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if backend is healthy
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -e "${YELLOW}⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start. Check logs with: docker-compose logs backend${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ InnovateX is ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}🌐 Available endpoints:${NC}"
echo -e "  ${GREEN}Backend API:${NC}      http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}         http://localhost:8000/docs"
echo -e "  ${GREEN}ReDoc:${NC}            http://localhost:8000/redoc"
echo -e "  ${GREEN}Health Check:${NC}     http://localhost:8000/health"
echo ""
echo -e "${BLUE}📊 Database:${NC}"
echo -e "  ${GREEN}PostgreSQL:${NC}       localhost:5432"
echo -e "  ${GREEN}Database:${NC}         innovatex_db"
echo -e "  ${GREEN}User:${NC}             postgres"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo -e "  ${GREEN}View logs:${NC}        docker-compose logs -f"
echo -e "  ${GREEN}Stop services:${NC}    docker-compose down"
echo -e "  ${GREEN}Restart:${NC}          docker-compose restart"
echo -e "  ${GREEN}Shell access:${NC}     docker-compose exec backend /bin/bash"
echo ""
echo -e "${YELLOW}💡 Tip: Use 'make help' to see all available commands${NC}"
echo ""

# Open browser (optional)
read -p "🌐 Open API docs in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        open http://localhost:8000/docs
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8000/docs
    else
        echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Setup complete! Happy coding!${NC}"

