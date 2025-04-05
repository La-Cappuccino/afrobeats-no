#!/bin/bash
#
# Afrobeats.no Agent System - Deployment Script
#
# This script automates the deployment process to various environments.
# Usage: ./scripts/deploy.sh [environment]
#   Environments: production, staging, development

set -e
trap 'echo "Error: Command failed at line $LINENO. Exiting..."; exit 1' ERR

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT="${1:-production}"
VALID_ENVIRONMENTS=("production" "staging" "development")

# Validate environment argument
if [[ ! " ${VALID_ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    echo -e "${RED}Error: Invalid environment '${ENVIRONMENT}'${NC}"
    echo -e "Valid environments: ${YELLOW}${VALID_ENVIRONMENTS[@]}${NC}"
    exit 1
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    Afrobeats.no Agent System Deployment    ${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"

# Build Docker image
echo -e "${BLUE}Building Docker image...${NC}"
IMAGE_NAME="afrobeatsno/agent-system:${ENVIRONMENT}"
docker build -t "${IMAGE_NAME}" .
echo -e "${GREEN}✓ Docker image built: ${IMAGE_NAME}${NC}"

# Push to registry if needed
if [[ "${ENVIRONMENT}" != "development" ]]; then
    echo -e "${BLUE}Pushing Docker image to registry...${NC}"
    docker push "${IMAGE_NAME}"
    echo -e "${GREEN}✓ Docker image pushed to registry${NC}"
fi

# Deploy based on environment
case "${ENVIRONMENT}" in
    production)
        echo -e "${BLUE}Deploying to production environment...${NC}"
        # Example for production deployment to cloud service
        if command -v kubectl &> /dev/null; then
            echo -e "${BLUE}Applying Kubernetes manifests...${NC}"
            kubectl apply -f k8s/production/
            echo -e "${GREEN}✓ Kubernetes manifests applied${NC}"
        else
            echo -e "${YELLOW}kubectl not found. Skipping Kubernetes deployment.${NC}"
            echo -e "${YELLOW}To deploy, run: kubectl apply -f k8s/production/${NC}"
        fi
        ;;
    staging)
        echo -e "${BLUE}Deploying to staging environment...${NC}"
        # Example for staging deployment
        if command -v kubectl &> /dev/null; then
            echo -e "${BLUE}Applying Kubernetes manifests...${NC}"
            kubectl apply -f k8s/staging/
            echo -e "${GREEN}✓ Kubernetes manifests applied${NC}"
        else
            echo -e "${YELLOW}kubectl not found. Skipping Kubernetes deployment.${NC}"
            echo -e "${YELLOW}To deploy, run: kubectl apply -f k8s/staging/${NC}"
        fi
        ;;
    development)
        echo -e "${BLUE}Starting local development environment...${NC}"
        docker-compose -f docker-compose.dev.yml up -d
        echo -e "${GREEN}✓ Local development environment started${NC}"
        echo -e "${YELLOW}To view logs: docker-compose -f docker-compose.dev.yml logs -f${NC}"
        echo -e "${YELLOW}To stop: docker-compose -f docker-compose.dev.yml down${NC}"
        ;;
esac

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    Deployment to ${ENVIRONMENT} completed!    ${NC}"
echo -e "${GREEN}============================================${NC}"