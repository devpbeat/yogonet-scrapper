#!/bin/bash
# Script to build, push, and deploy the Yogonet scraper to Cloud Run

# Source environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  source .env
else
  echo "Error: .env file not found"
  exit 1
fi

# Configuration
if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID not set in .env file"
  exit 1
fi

REGION="${REGION:-us-central1}"  # Default to us-central1 if not specified in .env
ARTIFACT_REPO="${ARTIFACT_REPO:-yogonet-images}"  # Default repo name
IMAGE_NAME="yogonet-scraper"
SERVICE_NAME="yogonet-scraper-service"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-yogonet-service-acc@$PROJECT_ID.iam.gserviceaccount.com}"

# Set the full image path for Artifact Registry
IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/$IMAGE_NAME:latest"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Ensure we're using the correct project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Configure Docker to use gcloud credentials for Artifact Registry
echo "Configuring Docker authentication to Artifact Registry..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Check if repository exists, create if it doesn't
if ! gcloud artifacts repositories describe $ARTIFACT_REPO --location=$REGION &> /dev/null; then
    echo "Creating Artifact Registry repository $ARTIFACT_REPO..."
    gcloud artifacts repositories create $ARTIFACT_REPO \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Yogonet scraper"
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_PATH .

# Push the image to Artifact Registry
echo "Pushing image to Artifact Registry..."
docker push $IMAGE_PATH

# Create temporary .env.yaml file for Cloud Run
echo "Creating deployment environment file..."
cat > .env.yaml << EOF
DATASET: "${DATASET}"
PROJECT_ID: "${PROJECT_ID}"
GOOGLE_APPLICATION_CREDENTIALS: "/app/google-application-credentials"
OPENAI_API_KEY: "${OPENAI_API_KEY}"
WRITE_TO_BIGQUERY: "${WRITE_TO_BIGQUERY}"
EOF

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_PATH \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 30m \
  --set-env-vars-file=.env.yaml \
  --service-account="$SERVICE_ACCOUNT"

# Clean up temporary file
echo "Cleaning up temporary files..."
rm .env.yaml

echo "Deployment completed! Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"