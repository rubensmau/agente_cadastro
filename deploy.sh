#!/bin/bash
# Deployment script for Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="registration-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Registration Agent - Cloud Run Deployment${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${YELLOW}Warning: Using default project ID${NC}"
    echo "Set your project ID with: export GCP_PROJECT_ID=your-actual-project-id"
    read -p "Enter your GCP Project ID: " PROJECT_ID
fi

# Set the GCP project
echo -e "${YELLOW}Setting GCP project: ${PROJECT_ID}${NC}"
gcloud config set project "${PROJECT_ID}"

# Enable required APIs
echo -e "\n${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com

# Build the Docker image
echo -e "\n${YELLOW}Building Docker image...${NC}"
docker build -t "${IMAGE_NAME}:latest" .

# Push to Google Container Registry
echo -e "\n${YELLOW}Pushing image to GCR...${NC}"
docker push "${IMAGE_NAME}:latest"

# Deploy to Cloud Run
echo -e "\n${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE_NAME}:latest" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --cpu=1 \
    --memory=512Mi \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars=SERVER_MODE=compliant

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --format='value(status.url)')

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nService URL: ${GREEN}${SERVICE_URL}${NC}"
echo -e "\nAvailable endpoints:"
echo -e "  - Agent Card: ${SERVICE_URL}/metadata"
echo -e "  - Health Check: ${SERVICE_URL}/health"
echo -e "  - Search: ${SERVICE_URL}/send_message (POST)"
echo -e "  - Human UI: ${SERVICE_URL}/"
echo -e "\nTest with:"
echo -e "  ${YELLOW}curl ${SERVICE_URL}/health${NC}"
echo -e "\n${GREEN}========================================${NC}\n"
