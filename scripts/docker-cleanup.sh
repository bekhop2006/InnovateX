#!/bin/bash

# InnovateX Docker Cleanup Script
# This script helps clean up Docker resources

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 InnovateX Docker Cleanup${NC}"
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Stop containers
if confirm "${YELLOW}Stop all InnovateX containers?${NC}"; then
    echo -e "${BLUE}Stopping containers...${NC}"
    docker-compose --profile tools down
    echo -e "${GREEN}✅ Containers stopped${NC}"
fi

# Remove volumes
if confirm "${YELLOW}Remove all volumes (WARNING: Database data will be lost!)?${NC}"; then
    echo -e "${RED}Removing volumes...${NC}"
    docker-compose --profile tools down -v
    echo -e "${GREEN}✅ Volumes removed${NC}"
fi

# Remove images
if confirm "${YELLOW}Remove InnovateX Docker images?${NC}"; then
    echo -e "${BLUE}Removing images...${NC}"
    docker-compose down --rmi local 2>/dev/null || true
    echo -e "${GREEN}✅ Images removed${NC}"
fi

# Clean Docker system
if confirm "${YELLOW}Clean unused Docker resources (system prune)?${NC}"; then
    echo -e "${BLUE}Cleaning Docker system...${NC}"
    docker system prune -f
    echo -e "${GREEN}✅ Docker system cleaned${NC}"
fi

# Show disk usage
echo ""
echo -e "${BLUE}💾 Current Docker disk usage:${NC}"
docker system df

echo ""
echo -e "${GREEN}🎉 Cleanup complete!${NC}"

