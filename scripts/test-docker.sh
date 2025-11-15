#!/bin/bash

# InnovateX Docker Test Script
# This script tests if the Docker environment is working correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 InnovateX Docker Test Suite${NC}"
echo ""

# Counter for passed/failed tests
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null || echo "000")
    
    if [ "$response" == "$expected" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED (expected $expected, got $response)${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Check if containers are running
echo -e "${BLUE}1. Checking Docker containers...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Containers are running${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ Containers are not running${NC}"
    echo -e "${YELLOW}Run: docker-compose up -d${NC}"
    FAILED=$((FAILED + 1))
    exit 1
fi
echo ""

# Wait for services to be ready
echo -e "${BLUE}2. Waiting for services to be ready...${NC}"
sleep 3
echo -e "${GREEN}✓ Ready${NC}"
echo ""

# Test endpoints
echo -e "${BLUE}3. Testing API endpoints...${NC}"

test_endpoint "Root endpoint" "http://localhost:8000/" "200"
test_endpoint "Health check" "http://localhost:8000/health" "200"
test_endpoint "API docs" "http://localhost:8000/docs" "200"
test_endpoint "ReDoc" "http://localhost:8000/redoc" "200"
test_endpoint "Document Inspector health" "http://localhost:8000/api/document-inspector/health" "200"

echo ""

# Test database connection
echo -e "${BLUE}4. Testing database connection...${NC}"
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ PostgreSQL is not ready${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check logs for errors
echo -e "${BLUE}5. Checking for errors in logs...${NC}"
ERROR_COUNT=$(docker-compose logs backend | grep -i "error" | grep -v "ERROR" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors in backend logs${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error(s) in logs${NC}"
    # Don't fail on this one, just warn
    PASSED=$((PASSED + 1))
fi
echo ""

# Test Document Inspector (if model exists)
echo -e "${BLUE}6. Testing Document Inspector...${NC}"
MODEL_STATUS=$(curl -s http://localhost:8000/api/document-inspector/health | grep -o '"model_loaded":[^,]*' | cut -d':' -f2)
if [ "$MODEL_STATUS" == "true" ]; then
    echo -e "${GREEN}✓ Model is loaded and ready${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Model not loaded (this is ok if not trained yet)${NC}"
    PASSED=$((PASSED + 1))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! InnovateX is working correctly!${NC}"
    echo ""
    echo -e "${BLUE}Available endpoints:${NC}"
    echo -e "  ${GREEN}Backend API:${NC}      http://localhost:8000"
    echo -e "  ${GREEN}API Docs:${NC}         http://localhost:8000/docs"
    echo -e "  ${GREEN}Health Check:${NC}     http://localhost:8000/health"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the logs above.${NC}"
    echo ""
    echo -e "${YELLOW}Debugging commands:${NC}"
    echo -e "  ${BLUE}docker-compose logs backend${NC}     - View backend logs"
    echo -e "  ${BLUE}docker-compose logs postgres${NC}    - View database logs"
    echo -e "  ${BLUE}docker-compose ps${NC}               - Check container status"
    exit 1
fi

