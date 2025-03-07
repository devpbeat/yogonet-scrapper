#!/bin/bash
# Comprehensive deployment script for Yogonet Scraper to Google Cloud Run

# Fail on any error
set -e

# Source environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  source .env
else
  echo "Error: .env file not found"
  exit 1
fi

# Validate required environment variables
REQUIRED_VARS=("PROJECT_ID" "REGION")
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: $var is not set in .env file"
    exit 1
  fi
done

# Set default values if not provided
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-yogonet-scraper-service}"
IMAGE_NAME="${IMAGE_NAME:-yogonet-scraper}"

# Full image path for Artifact Registry
FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest"

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { 
    echo "gcloud CLI is not installed. Please install Google Cloud SDK."
    exit 1 
}

command -v docker >/dev/null 2>&1 || { 
    echo "Docker is not installed. Please install Docker."
    exit 1 
}

# Set the Google Cloud project
echo "Setting Google Cloud project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "Checking/Creating Artifact Registry repository..."
if ! gcloud artifacts repositories describe "${IMAGE_NAME}" \
    --location="${REGION}" 2>/dev/null; then
    gcloud artifacts repositories create "${IMAGE_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Repository for Yogonet Scraper"
fi

# Configure Docker to use Artifact Registry
echo "Configuring Docker to use Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev"

# Build the Docker image
echo "Building Docker image..."
docker buildx build -t "${FULL_IMAGE_PATH}" .

# Push the image to Artifact Registry
echo "Pushing image to Artifact Registry..."
docker push "${FULL_IMAGE_PATH}"

# Prepare environment variables file for Cloud Run
echo "Creating deployment environment file..."
cat > .env.yaml << EOF
DATASET: "${DATASET}"
PROJECT_ID: "${PROJECT_ID}"
GOOGLE_APPLICATION_CREDENTIALS: "${GOOGLE_APPLICATION_CREDENTIALS}"
OPENAI_API_KEY: "${OPENAI_API_KEY}"
WRITE_TO_BIGQUERY: "${WRITE_TO_BIGQUERY}"
EOF

# Create bigquery table with the dataset name
if [ "${WRITE_TO_BIGQUERY}" = "true" ]; then
    if ! bq ls --dataset_id "${PROJECT_ID}:${DATASET}" >/dev/null 2>&1; then
      echo "Creating BigQuery table..."
      bq mk --dataset "${PROJECT_ID}:${DATASET}"
      bq mk --table "${PROJECT_ID}:${DATASET}.yogonet_articles" \
        title:STRING,kicker:STRING,link:STRING,image:STRING,date:STRING,scrape_timestamp:TIMESTAMP,title_word_count:INTEGER,title_char_count:INTEGER,capitalized_words:STRING,persons:STRING,organizations:STRING,locations:STRING
    fi

fi
# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${FULL_IMAGE_PATH}" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 30m \
    --env-vars-file=.env.yaml \
    --service-account="${SERVICE_ACCOUNT}"

# Clean up temporary file
echo "Cleaning up temporary files..."
rm .env.yaml

# Display service URL
echo "Deployment completed! Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)"