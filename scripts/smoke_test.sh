#!/bin/bash
# Smoke test script for Munqith deployment
# Tests basic functionality: docker build, database connection, migrations, health check

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_URL="http://localhost:8000"
HEALTH_ENDPOINT="${API_URL}/health"
DOCKER_COMPOSE="docker-compose"

echo "======================================================================"
echo "MUNQITH SMOKE TEST"
echo "======================================================================"

# Check prerequisites
echo -e "\n${YELLOW}Phase 1: Prerequisite Check${NC}"
echo "----------------------------------------------------------------------"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker available${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose available${NC}"

if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ curl not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ curl available${NC}"

# Navigate to project directory
cd "${PROJECT_DIR}"

# Stop any existing containers
echo -e "\n${YELLOW}Phase 2: Cleanup${NC}"
echo "----------------------------------------------------------------------"
echo "Stopping any existing containers..."
${DOCKER_COMPOSE} down -v 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Build and start containers
echo -e "\n${YELLOW}Phase 3: Container Build & Start${NC}"
echo "----------------------------------------------------------------------"
echo "Building Docker image and starting services..."
${DOCKER_COMPOSE} up -d --build 2>&1 | grep -E "(Building|Creating|Starting|pull|Layer|Step)" || true

# Wait for database to be ready
echo -e "\n${YELLOW}Phase 4: Database Readiness${NC}"
echo "----------------------------------------------------------------------"
MAX_ATTEMPTS=30
ATTEMPT=0

echo "Waiting for PostgreSQL to be ready..."
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec munqith_postgres pg_isready -U munqith > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    sleep 1
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    ${DOCKER_COMPOSE} logs postgres
    ${DOCKER_COMPOSE} down -v
    exit 1
fi

# Run migrations
echo -e "\n${YELLOW}Phase 5: Database Migrations${NC}"
echo "----------------------------------------------------------------------"
echo "Running Alembic migrations..."

MIGRATION_OUTPUT=$(docker exec munqith_api sh -c "alembic upgrade head 2>&1" || echo "migration failed")
if echo "$MIGRATION_OUTPUT" | grep -q "FAILED\|ERROR"; then
    echo -e "${RED}✗ Migrations failed${NC}"
    echo "$MIGRATION_OUTPUT"
    ${DOCKER_COMPOSE} logs api
    ${DOCKER_COMPOSE} down -v
    exit 1
fi
echo -e "${GREEN}✓ Migrations completed${NC}"

# Wait for API to be ready
echo -e "\n${YELLOW}Phase 6: API Readiness${NC}"
echo "----------------------------------------------------------------------"
ATTEMPT=0
MAX_ATTEMPTS=30

echo "Waiting for API to be ready..."
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf "${HEALTH_ENDPOINT}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    sleep 1
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}✗ API failed to start${NC}"
    ${DOCKER_COMPOSE} logs api
    ${DOCKER_COMPOSE} down -v
    exit 1
fi

# Test health endpoint
echo -e "\n${YELLOW}Phase 7: Health Check${NC}"
echo "----------------------------------------------------------------------"
HEALTH_RESPONSE=$(curl -s "${HEALTH_ENDPOINT}")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
    ${DOCKER_COMPOSE} logs api
    ${DOCKER_COMPOSE} down -v
    exit 1
fi

# Optional: Test basic API functionality
echo -e "\n${YELLOW}Phase 8: Basic API Validation (Optional)${NC}"
echo "----------------------------------------------------------------------"

# Check if API endpoints are accessible
echo "Checking API documentation..."
if curl -sf "${API_URL}/openapi.json" > /dev/null; then
    echo -e "${GREEN}✓ API documentation available${NC}"
else
    echo -e "${YELLOW}⚠ API documentation not accessible${NC}"
fi

# Summary
echo -e "\n======================================================================"
echo -e "${GREEN}✓ SMOKE TEST PASSED${NC}"
echo "======================================================================"
echo ""
echo "Services running:"
${DOCKER_COMPOSE} ps

echo ""
echo "API available at: ${API_URL}"
echo "Health check:     ${HEALTH_ENDPOINT}"
echo ""
echo "To view logs:     docker-compose logs -f"
echo "To stop services: docker-compose down"

exit 0
