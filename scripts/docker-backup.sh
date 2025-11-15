#!/bin/bash

# InnovateX Docker Backup Script
# This script backs up the PostgreSQL database

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}💾 InnovateX Database Backup${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Create backup directory
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/innovatex_backup_$TIMESTAMP.sql"

echo -e "${BLUE}📦 Creating backup...${NC}"

# Check if container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${RED}❌ PostgreSQL container is not running${NC}"
    exit 1
fi

# Create backup
docker-compose exec -T postgres pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-innovatex_db} > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created successfully!${NC}"
    echo -e "${GREEN}📁 File: $BACKUP_FILE${NC}"
    
    # Show file size
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${BLUE}📊 Size: $SIZE${NC}"
    
    # Compress backup
    if command -v gzip &> /dev/null; then
        echo -e "${BLUE}🗜️  Compressing backup...${NC}"
        gzip $BACKUP_FILE
        echo -e "${GREEN}✅ Compressed: ${BACKUP_FILE}.gz${NC}"
        COMPRESSED_SIZE=$(du -h ${BACKUP_FILE}.gz | cut -f1)
        echo -e "${BLUE}📊 Compressed size: $COMPRESSED_SIZE${NC}"
    fi
    
    # Clean old backups (keep last 7)
    echo ""
    echo -e "${BLUE}🧹 Cleaning old backups (keeping last 7)...${NC}"
    ls -t $BACKUP_DIR/innovatex_backup_*.sql.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
    
    BACKUP_COUNT=$(ls -1 $BACKUP_DIR/innovatex_backup_*.sql.gz 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ Total backups: $BACKUP_COUNT${NC}"
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Backup complete!${NC}"

