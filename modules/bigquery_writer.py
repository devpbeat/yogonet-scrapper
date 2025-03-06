#!/usr/bin/env python3
"""
Module for writing scraped data to BigQuery.
"""
import os
import logging
import pandas as pd
import pandas_gbq
from datetime import datetime

logger = logging.getLogger(__name__)

class BigQueryWriter:
    """Class for writing data to BigQuery."""
    
    def __init__(self):
        """Initialize the BigQuery writer."""
        self.dataset = os.environ.get('DATASET', 'yogonet')
        self.project_id = os.environ.get('PROJECT_ID')
        
        if not self.project_id:
            logger.warning("PROJECT_ID environment variable not set. Using default project.")
    
    def write_articles(self, articles, table_name='articles'):
        """
        Write articles to BigQuery table with post-processed metrics.
        
        Args:
            articles: List of article dictionaries
            table_name: Name of the BigQuery table (default: 'articles')
        """
        if not articles:
            logger.warning("No articles to write to BigQuery.")
            return
        
        try:
            # Convert articles to DataFrame
            df = pd.DataFrame(articles)
            
            # Add timestamp column
            df['scrape_timestamp'] = datetime.now()
            
            # Post-processing metrics
            df['title_word_count'] = df['title'].apply(self._count_words)
            df['title_char_count'] = df['title'].apply(len)
            df['capitalized_words'] = df['title'].apply(self._find_capitalized_words)
            
            # Define schema for BigQuery
            schema = [
                {'name': 'title', 'type': 'STRING'},
                {'name': 'kicker', 'type': 'STRING'},
                {'name': 'link', 'type': 'STRING'},
                {'name': 'image', 'type': 'STRING'},
                {'name': 'scrape_timestamp', 'type': 'TIMESTAMP'},
                {'name': 'title_word_count', 'type': 'INTEGER'},
                {'name': 'title_char_count', 'type': 'INTEGER'},
                {'name': 'capitalized_words', 'type': 'STRING'}
            ]
            
            # Full table name
            full_table_name = f'{self.dataset}.{table_name}'
            
            logger.info(f"Writing {len(df)} articles to BigQuery table {full_table_name}")
            
            # Prepare capitalized words as comma-separated string for BigQuery
            df['capitalized_words'] = df['capitalized_words'].apply(
                lambda x: ','.join(x) if isinstance(x, list) else x
            )
            
            # Write to BigQuery
            pandas_gbq.to_gbq(
                df,
                full_table_name,
                project_id=self.project_id,
                table_schema=schema,
                if_exists='append'
            )
            
            logger.info(f"Successfully wrote {len(df)} articles to {full_table_name}")
            
            # Optional: Generate and log summary
            self._log_article_summary(df)
            
            return df
        
        except Exception as e:
            logger.error(f"Error writing to BigQuery: {e}")
            return None
    
    def _count_words(self, text):
        """
        Count the number of words in the given text.
        
        :param text: Input text
        :return: Number of words
        """
        try:
            return len(str(text).split())
        except Exception as e:
            logger.warning(f"Error counting words in text '{text}': {e}")
            return 0
    
    def _find_capitalized_words(self, text):
        """
        Find words that start with a capital letter.
        
        :param text: Input text
        :return: List of capitalized words
        """
        import re
        try:
            # Use regex to find words starting with a capital letter
            return re.findall(r'\b[A-Z][a-z]*\b', str(text))
        except Exception as e:
            logger.warning(f"Error finding capitalized words in text '{text}': {e}")
            return []
    
    def _log_article_summary(self, df):
        """
        Log a summary of the processed articles.
        
        :param df: Processed DataFrame
        """
        try:
            logger.info("Article Processing Summary:")
            logger.info(f"Total Articles: {len(df)}")
            logger.info(f"Average Title Word Count: {df['title_word_count'].mean():.2f}")
            logger.info(f"Average Title Character Count: {df['title_char_count'].mean():.2f}")
            
            # Find most common capitalized words
            all_capitalized_words = [word for words in df['capitalized_words'] for word in words.split(',') if word]
            from collections import Counter
            top_capitalized = Counter(all_capitalized_words).most_common(5)
            
            logger.info("Top Capitalized Words:")
            for word, count in top_capitalized:
                logger.info(f"  {word}: {count}")
        
        except Exception as e:
            logger.error(f"Error generating article summary: {e}")