# Yogonet Scrapper

A web scrapper for Yogonet International that extracts news articles using Selenium and AI-based element selection, with the ability to store data in Google BigQuery.

## Features

- Docker-based setup for easy deployment
- Selenium-based web scraping
- AI-assisted dynamic element selection
- Extracts article titles, kickers, links, and images
- Stores scraped data in Google BigQuery

## Requirements

- Docker
- Internet connection
- Google Cloud account (for BigQuery integration)

## Setup and Usage

1. Clone this repository:
```bash
git clone https://github.com/yourusername/yogonet-scrapper.git
cd yogonet-scrapper
```

2. Build the Docker image:
```bash
docker build -t yogonet-scrapper .
```

3. Run the scrapper:
```bash
docker run yogonet-scrapper
```

4. To store data in BigQuery, you'll need to set some environment variables:
```bash
docker run \
  -e DATASET=your_dataset \
  -e PROJECT_ID=your_project_id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v /path/to/your/credentials.json:/app/credentials.json \
  yogonet-scrapper
```

5. (Optional) To use the AI-based selector feature, set your OpenAI API key:
```bash
docker run -e OPENAI_API_KEY=your_api_key_here yogonet-scrapper
```

## Environment Variables

- `DATASET`: BigQuery dataset name (default: "yogonet")
- `PROJECT_ID`: Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account key file
- `OPENAI_API_KEY`: OpenAI API key for AI-based selector
- `WRITE_TO_BIGQUERY`: Set to "false" to skip writing to BigQuery (default: "true")

## How it Works

The scrapper works by:
1. Launching a headless Chrome browser
2. Navigating to Yogonet International
3. Using either pre-defined selectors or AI-based selectors to find news articles
4. Extracting the title, kicker, link, and image from each article
5. Storing the results in BigQuery (if enabled)
6. Printing the results

## BigQuery Integration

The scrapper uses pandas-gbq to write the scraped data to a BigQuery table. The table schema includes:
- title (STRING)
- kicker (STRING)
- link (STRING)
- image (STRING)
- scrape_timestamp (TIMESTAMP)

## AI-Assisted Dynamic Scraping

The scrapper uses OpenAI's GPT model to analyze the HTML structure and identify the correct selectors for article elements. This helps the scrapper adapt to changes in the website's structure over time.

If no OpenAI API key is provided, the scrapper falls back to default selectors.