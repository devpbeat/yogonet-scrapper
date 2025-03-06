#!/bin/bash
# Script to run the Yogonet scraper locally using Docker

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found"
  echo "Please create a .env file with your configuration"
  exit 1
fi

# Source environment variables
source .env

# Check if GOOGLE_APPLICATION_CREDENTIALS is set and the file exists
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "Warning: GOOGLE_APPLICATION_CREDENTIALS not set in .env"
  CREDS_FILE="not-set"
else
  CREDS_FILE=$(basename "$GOOGLE_APPLICATION_CREDENTIALS")
  if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ "$WRITE_TO_BIGQUERY" = "true" ]; then
    echo "Warning: Google credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
    echo "BigQuery integration may not work properly"
  fi
fi

# Build the Docker image if needed
# echo "Checking if Docker image exists..."
# if [[ "$(docker images -q yogonet-scraper 2> /dev/null)" == "" ]]; then
# fi

echo "Building Docker image..."
docker build -t yogonet-scraper .
# Run the container
echo "Running Yogonet scraper..."
echo "Writing to BigQuery: $WRITE_TO_BIGQUERY"

if [ "$WRITE_TO_BIGQUERY" = "true" ]; then
  echo "Using Google credentials: $CREDS_FILE"
  docker run --rm \
    --env-file .env \
    -v "$GOOGLE_APPLICATION_CREDENTIALS:/app/$CREDS_FILE" \
    yogonet-scraper
else
  docker run --rm \
    --env-file .env \
    yogonet-scraper
fi

echo "Scraper run completed"