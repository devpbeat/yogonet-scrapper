#!/usr/bin/env python3
"""
Main entry point for the Yogonet International Web Scraper.
"""

import os
import sys
import logging
from datetime import datetime

# Ensure project root is in Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scrapper import YogonetScraper
from modules.bigquery_writer import BigQueryWriter
from modules.post_processing import ArticlePostProcessor
from modules.named_entity import NamedEntityExtractor

def setup_logging():
    """Configure comprehensive logging."""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"yogonet_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_filename

def main():
    """Main execution function."""
    # Set up logging
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    scraper = None
    
    try:
        logger.info("🚀 Starting Yogonet International Web Scraper")
        logger.info("=" * 50)
        
        # Initialize components
        logger.info("Initializing scrapers and processors...")
        scraper = YogonetScraper()
        post_processor = ArticlePostProcessor()
        entity_extractor = NamedEntityExtractor()
        bq_writer = BigQueryWriter()
        
        # Scrape articles
        logger.info("📡 Initiating web scraping...")
        articles = scraper.scrape_articles()
        
        if not articles:
            logger.warning("⚠️ No articles were scraped. Exiting.")
            return None
        
        logger.info(f"📊 Scraped {len(articles)} articles")
        
        # Extract named entities
        logger.info("🏷️ Extracting named entities...")
        articles_with_entities = entity_extractor.extract_entities_from_articles(articles)
        
        # Process articles
        logger.info("🔍 Processing scraped articles...")
        processed_df = post_processor.process_articles(articles_with_entities)
        
        # Generate summary report
        summary_report = post_processor.generate_summary_report(processed_df)
        
        # Log detailed summary
        logger.info("\n📈 Article Processing Summary:")
        logger.info(f"Total Articles: {summary_report.get('total_articles', 0)}")
        logger.info(f"Avg Title Word Count: {summary_report.get('avg_title_word_count', 0):.2f}")
        logger.info(f"Avg Title Character Count: {summary_report.get('avg_title_char_count', 0):.2f}")
        
        # Log most common capitalized words
        logger.info("\n🔤 Most Common Capitalized Words:")
        for word, count in summary_report.get('most_common_capitalized_words', {}).items():
            logger.info(f"  {word}: {count}")
            
        # Write to BigQuery (conditional based on environment)
        if os.environ.get('WRITE_TO_BIGQUERY', 'true').lower() == 'true':
            logger.info("💾 Writing articles to BigQuery...")
            result = bq_writer.write_articles(articles_with_entities)
            if result is not None:
                logger.info("✅ Articles successfully written to BigQuery")
            else:
                logger.warning("⚠️ Failed to write articles to BigQuery")
        else:
            logger.info("⏩ Skipping BigQuery write (WRITE_TO_BIGQUERY is not 'true')")
        
        logger.info("\n🎉 Scraping and Processing Completed Successfully!")
        logger.info(f"📄 Detailed logs available at: {log_file}")
        
        return processed_df, summary_report
    
    except Exception as e:
        logger.error(f"❌ Critical Error during scraping: {e}", exc_info=True)
        return None, None
    
    finally:
        if scraper:
            try:
                scraper.close()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
        
        logger.info("🔚 Scraper process completed.")

def cli():
    """
    Command-line interface entry point.
    Provides a way to run the scraper from the command line.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Yogonet International Web Scraper")
    parser.add_argument(
        '--no-bigquery', 
        action='store_true', 
        help="Disable writing to BigQuery"
    )
    
    args = parser.parse_args()
    
    if args.no_bigquery:
        os.environ['WRITE_TO_BIGQUERY'] = 'false'
    
    main()

if __name__ == "__main__":
    cli()