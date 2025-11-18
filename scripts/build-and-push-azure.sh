#!/bin/bash
# ==============================================================================
# Build and Push Docker Images to Azure Container Registry
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ACR_NAME="kenislabsregistry"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
BACKEND_IMAGE="${ACR_LOGIN_SERVER}/arka-backend"
FRONTEND_IMAGE="${ACR_LOGIN_SERVER}/arka-frontend"
TAG="${1:-latest}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Arka MCP Gateway - Azure Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login...${NC}"
if ! az account show > /dev/null 2>&1; then
    echo -e "${YELLOW}Not logged in to Azure. Running 'az login'...${NC}"
    az login
fi

# Login to ACR
echo -e "${YELLOW}Logging in to Azure Container Registry...${NC}"
az acr login --name ${ACR_NAME}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Build backend
echo -e "${YELLOW}Building backend image for AMD64...${NC}"
docker build \
  --platform linux/amd64 \
  -t ${BACKEND_IMAGE}:${TAG} \
  -t ${BACKEND_IMAGE}:latest \
  -f backend/Dockerfile \
  ./backend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed${NC}"
    exit 1
fi

# Build frontend
echo -e "${YELLOW}Building frontend image for AMD64...${NC}"
docker build \
  --platform linux/amd64 \
  -t ${FRONTEND_IMAGE}:${TAG} \
  -t ${FRONTEND_IMAGE}:latest \
  -f frontend/Dockerfile \
  ./frontend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

# Push backend
echo -e "${YELLOW}Pushing backend image to ACR...${NC}"
docker push ${BACKEND_IMAGE}:${TAG}
docker push ${BACKEND_IMAGE}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image pushed successfully${NC}"
else
    echo -e "${RED}✗ Backend push failed${NC}"
    exit 1
fi

# Push frontend
echo -e "${YELLOW}Pushing frontend image to ACR...${NC}"
docker push ${FRONTEND_IMAGE}:${TAG}
docker push ${FRONTEND_IMAGE}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image pushed successfully${NC}"
else
    echo -e "${RED}✗ Frontend push failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All images built and pushed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Images pushed:${NC}"
echo "  - ${BACKEND_IMAGE}:${TAG}"
echo "  - ${BACKEND_IMAGE}:latest"
echo "  - ${FRONTEND_IMAGE}:${TAG}"
echo "  - ${FRONTEND_IMAGE}:latest"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. SSH into your Azure VM"
echo "  2. Pull the latest images:"
echo "     docker-compose -f docker-compose.production.yml pull"
echo "  3. Restart services:"
echo "     docker-compose -f docker-compose.production.yml up -d"
echo ""