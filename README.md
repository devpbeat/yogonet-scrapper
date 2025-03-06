# Yogonet Scraper

A web scraper for **Yogonet International** that extracts news articles using **Selenium** and **AI-based element selection**, with the ability to store data in **Google BigQuery** and deployed to **Google Cloud Run**.

## 🚀 Features

- **Docker-based** setup for easy deployment
- **Selenium-based web scraping**
- **AI-assisted dynamic element selection**
- Extracts **article titles, kickers, links, and images**
- Stores scraped data in **Google BigQuery**
- **Automated deployment** to Google Cloud Run

---

## 📌 Requirements

- **Docker**
- **Google Cloud SDK (`gcloud` CLI)**
- **Google Cloud account** with:
  - ✅ Cloud Run API enabled
  - ✅ Container Registry API enabled
  - ✅ BigQuery API enabled
  - ✅ Service account with appropriate permissions

---

## 📂 Project Structure

```plaintext
yogonet-scraper/ 
├── Dockerfile # Container configuration 
├── requirements.txt # Python dependencies 
├── main.py # Entry point script 
├── scraper.py # Web scraping implementation 
├── ai_selector.py # AI-based selector implementation 
├── bigquery_writer.py # BigQuery integration 
├── deploy.sh # Deployment script └── README.md # Documentation
```


---

## 🔧 Setup and Local Usage

1️. Clone this repository:
```sh
git clone https://github.com/yourusername/yogonet-scraper.git
cd yogonet-scraper
```
2️. Create a .env file with the same structure as `.env.example`:
```sh
cp .env.example .env
```
3️. Build the Docker image locally:   
```sh
docker build -t yogonet-scraper .
```

4️. Run the scraper locally with the environment file:
```sh
docker run --env-file .env -v /path/to/your/credentials.json:/app/google-application-credentials yogonet-scraper
```
For local testing without external services, set WRITE_TO_BIGQUERY="false" in your .env file.


## ☁️ Google Cloud Deployment
🔹 Prerequisites
1. Install Google Cloud SDK:
https://cloud.google.com/sdk/docs/install

2. Initialize and authenticate gcloud:
```sh
gcloud init
gcloud auth login
```

3. Enable required APIs:
```sh
gcloud services enable run.googleapis.com containerregistry.googleapis.com bigquery.googleapis.com
```

4. Create a service account and grant necessary permissions:
```sh
gcloud iam service-accounts create yogonet-scraper-sa
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:yogonet-scraper-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

5. Create a BigQuery dataset:
```sh
bq mk --dataset yogonet
```


🚀 Deployment Steps
1. Edit your .env file with your actual Google Cloud details.
2. Make the deploy script executable:
```sh
chmod +x deploy.sh
```
3. Run the deployment script:
```sh
./deploy.sh
```

### This script will: 
- Build the Docker image 
- Push it to Google Container Registry
- Deploy it to Google Cloud Run
- Output the service URL

# ⚙️ Environment Variables
| Variable                       | Description                                           | Default Value  |
|--------------------------------|-------------------------------------------------------|----------------|
| `DATASET`                      | BigQuery dataset name                                 | "yogonet"      |
| `PROJECT_ID`                   | Google Cloud project ID                               | Required       |
| `REGION`                       | Your preferred GCP region                             | "us-central1"  |
| `SERVICE_ACCOUNT`              | Service account email for Cloud Run                   | Required       |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud service account key file         | Required       |
| `OPENAI_API_KEY`               | OpenAI API key for AI-based selector                  | Required       |
| `WRITE_TO_BIGQUERY`            | Set "false" to skip writing to BigQuery               | "true"         |


# 🔍 How It Works

1. Launches a headless Chrome browser
2. Navigates to Yogonet International
3. Uses pre-defined or AI-based selectors to find news articles
4. Extracts the title, kicker, link, and image from each article
5. Stores results in BigQuery (if enabled)
6. Prints the extracted data

# ⏳ Scheduling Periodic Runs
To run the scraper daily, use Google Cloud Scheduler:
```sh 
gcloud scheduler jobs create http yogonet-daily-scrape \
  --schedule="0 9 * * *" \
  --uri="YOUR_CLOUD_RUN_SERVICE_URL" \
  --http-method=GET \
  --time-zone="UTC"
```
This example runs the scraper every day at 9:00 AM UTC.

# 🔍 Troubleshooting

### **Authentication Issues**
Ensure your service account has the correct permissions.
### **Scraper Failures**
Check Cloud Run logs for error details.
### **BigQuery Issues**
Verify that your dataset exists and the service account has access.

### 📜 For detailed error logs, use:
```sh
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=yogonet-scraper-service" --limit=10
```
