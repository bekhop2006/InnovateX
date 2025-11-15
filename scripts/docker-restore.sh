#!/bin/bash

# InnovateX Docker Restore Script
# This script restores the PostgreSQL database from a backup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📥 InnovateX Database Restore${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

BACKUP_DIR="backups"

# Check if backups directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backups directory not found${NC}"
    exit 1
fi

# List available backups
echo -e "${BLUE}📋 Available backups:${NC}"
echo ""

backups=($(ls -t $BACKUP_DIR/innovatex_backup_*.sql.gz 2>/dev/null))

if [ ${#backups[@]} -eq 0 ]; then
    # Check for uncompressed backups
    backups=($(ls -t $BACKUP_DIR/innovatex_backup_*.sql 2>/dev/null))
    
    if [ ${#backups[@]} -eq 0 ]; then
        echo -e "${RED}❌ No backups found${NC}"
        exit 1
    fi
fi

# Display backups with numbers
for i in "${!backups[@]}"; do
    SIZE=$(du -h "${backups[$i]}" | cut -f1)
    echo -e "${GREEN}$((i+1)))${NC} ${backups[$i]} (${SIZE})"
done

echo ""
read -p "Enter backup number to restore (or 0 to cancel): " backup_num

if [ "$backup_num" -eq 0 ] 2>/dev/null; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

if [ "$backup_num" -lt 1 ] || [ "$backup_num" -gt ${#backups[@]} ] 2>/dev/null; then
    echo -e "${RED}❌ Invalid backup number${NC}"
    exit 1
fi

BACKUP_FILE="${backups[$((backup_num-1))]}"

echo ""
echo -e "${YELLOW}⚠️  WARNING: This will replace all data in the database!${NC}"
read -p "Are you sure you want to continue? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Check if container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${RED}❌ PostgreSQL container is not running${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Restoring from: $BACKUP_FILE${NC}"

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${BLUE}🗜️  Decompressing backup...${NC}"
    TEMP_FILE="${BACKUP_FILE%.gz}.temp"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    RESTORE_FILE="$TEMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Drop and recreate database
echo -e "${BLUE}🗑️  Dropping existing database...${NC}"
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-postgres} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-innovatex_db};" postgres

echo -e "${BLUE}🆕 Creating new database...${NC}"
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-postgres} -c "CREATE DATABASE ${POSTGRES_DB:-innovatex_db};" postgres

# Restore backup
echo -e "${BLUE}📥 Restoring data...${NC}"
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-innovatex_db} < "$RESTORE_FILE"

# Clean up temp file
if [ -f "$TEMP_FILE" ]; then
    rm -f "$TEMP_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database restored successfully!${NC}"
    
    # Restart backend to apply changes
    echo -e "${BLUE}🔄 Restarting backend...${NC}"
    docker-compose restart backend
    
    echo ""
    echo -e "${GREEN}🎉 Restore complete!${NC}"
else
    echo -e "${RED}❌ Restore failed${NC}"
    exit 1
fi

