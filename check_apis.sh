#!/bin/bash

# Check if APIs are enabled
check_api_enabled() {
    local api_name=$1
    if ! gcloud services list --enabled | grep -q "$api_name"; then
        echo "Enabling $api_name..."
        gcloud services enable "$api_name"
    else
        echo "$api_name is already enabled."
    fi
}

# List of APIs to check
APIS=(
    "artifactregistry.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "cloudbuild.googleapis.com"
)

# Check and enable APIs
for api in "${APIS[@]}"; do
    check_api_enabled "$api"
done