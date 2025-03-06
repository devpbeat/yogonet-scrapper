#!/usr/bin/env python3
"""
Main entry point for the Yogonet scraper application.
"""
import os
import time
import logging
from modules.scrapper import YogonetScraper
from modules.bigquery_writer import BigQueryWriter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the scraper."""
    logger.info("Starting Yogonet scraper...")
    
    # Initialize the scraper
    scraper = YogonetScraper()
    
    # Initialize the BigQuery writer
    bq_writer = BigQueryWriter()
    
    try:
        # Run the scraper
        articles = scraper.scrape_articles()
        
        # Print summary
        logger.info(f"Found {len(articles)} articles")
        for i, article in enumerate(articles[:5], 1):
            logger.info(f"Article {i}:")
            logger.info(f"  Title: {article['title']}")
            logger.info(f"  Kicker: {article['kicker']}")
            logger.info(f"  Link: {article['link']}")
            logger.info(f"  Image: {article['image']}")
        
        # Write articles to BigQuery
        if os.environ.get('WRITE_TO_BIGQUERY', 'true').lower() == 'true':
            bq_writer.write_articles(articles)
        else:
            logger.info("Skipping BigQuery write (WRITE_TO_BIGQUERY is not 'true')")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
    finally:
        # Clean up
        scraper.close()
        logger.info("Scraper finished")

if __name__ == "__main__":
    main()