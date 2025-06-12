#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏋️‍♂️ Cyborg Coach Docker Setup${NC}"
echo "=================================="

# Check if Docker is installed and running
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}📝 Creating .env file from template...${NC}"
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${GREEN}✅ .env file created from env.example${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
    else
        echo -e "\n${YELLOW}Creating basic .env file...${NC}"
        cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cyborg_coach

# API Configuration
API_PORT=8000
LOG_LEVEL=debug

# Optional: Ollama for local models
OLLAMA_BASE_URL=http://host.docker.internal:11434
EOF
        echo -e "${GREEN}✅ Basic .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
    fi
    
    echo -e "\n${RED}🛑 Please configure your .env file before continuing.${NC}"
    echo -e "   Add your OpenAI API key to the OPENAI_API_KEY variable."
    echo -e "   Then run this script again.\n"
    exit 0
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo -e "\n${RED}🛑 Please set your OPENAI_API_KEY in the .env file${NC}"
    echo -e "   Edit .env and replace 'your_openai_api_key_here' with your actual API key.\n"
    exit 0
fi

echo -e "${GREEN}✅ .env file configured${NC}"

# Clean up any existing containers
echo -e "\n${YELLOW}🧹 Cleaning up existing containers...${NC}"
docker-compose down -v 2>/dev/null || true

# Build and start services
echo -e "\n${YELLOW}🔨 Building and starting services...${NC}"
docker-compose up --build -d

# Function to check service health
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo -e "\n${YELLOW}🔍 Checking $service health...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep "healthy" > /dev/null; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        elif docker-compose ps $service | grep "unhealthy" > /dev/null; then
            echo -e "${RED}❌ $service is unhealthy${NC}"
            return 1
        else
            echo -e "   Attempt $attempt/$max_attempts: Waiting for $service..."
            sleep 2
            ((attempt++))
        fi
    done
    
    echo -e "${RED}❌ $service health check timed out${NC}"
    return 1
}

# Check database health
if check_service_health "postgres"; then
    echo -e "${GREEN}✅ Database is ready${NC}"
else
    echo -e "${RED}❌ Database failed to start properly${NC}"
    echo -e "\n${YELLOW}📋 Database logs:${NC}"
    docker-compose logs postgres
    exit 1
fi

# Check API health
if check_service_health "api"; then
    echo -e "${GREEN}✅ API is ready${NC}"
else
    echo -e "${RED}❌ API failed to start properly${NC}"
    echo -e "\n${YELLOW}📋 API logs:${NC}"
    docker-compose logs api
    exit 1
fi

# Check UI health
if check_service_health "ui"; then
    echo -e "${GREEN}✅ UI is ready${NC}"
else
    echo -e "${RED}❌ UI failed to start properly${NC}"
    echo -e "\n${YELLOW}📋 UI logs:${NC}"
    docker-compose logs ui
    exit 1
fi

# Final verification
echo -e "\n${YELLOW}🔍 Final verification...${NC}"

# Test API endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API health endpoint responding${NC}"
else
    echo -e "${RED}❌ API health endpoint not responding${NC}"
fi

# Test UI endpoint
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ UI health endpoint responding${NC}"
else
    echo -e "${RED}❌ UI health endpoint not responding${NC}"
fi

echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "\n${BLUE}📍 Access your applications:${NC}"
echo -e "   • 🔧 GraphQL API: ${YELLOW}http://localhost:8000/graphql${NC}"
echo -e "   • 📊 API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   • 🖥️  Streamlit UI: ${YELLOW}http://localhost:8501${NC}"
echo -e "   • 🗄️  PostgreSQL: ${YELLOW}localhost:5432${NC}"

echo -e "\n${BLUE}🔧 Useful commands:${NC}"
echo -e "   • View logs: ${YELLOW}docker-compose logs [service]${NC}"
echo -e "   • Stop services: ${YELLOW}docker-compose down${NC}"
echo -e "   • Restart services: ${YELLOW}docker-compose restart${NC}"
echo -e "   • Clean rebuild: ${YELLOW}docker-compose down -v && docker-compose up --build${NC}"

echo -e "\n${GREEN}✅ Happy coaching! 🏋️‍♂️${NC}" 