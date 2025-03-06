#!/usr/bin/env python3
"""
Module for writing scraped data to BigQuery with enhanced entity extraction.
"""
import os
import logging
import pandas as pd
import pandas_gbq
from datetime import datetime
from typing import List, Dict, Optional

class BigQueryWriter:
    """Class for writing data to BigQuery with named entity support."""
    
    def __init__(self):
        """Initialize the BigQuery writer."""
        self.dataset = os.environ.get('DATASET', 'yogonet')
        self.project_id = os.environ.get('PROJECT_ID')
        
        if not self.project_id:
            logging.warning("PROJECT_ID environment variable not set. Using default project.")
    
    def write_articles(self, 
                       articles: List[Dict], 
                       table_name: str = 'articles') -> Optional[pd.DataFrame]:
        """
        Write articles to BigQuery table with comprehensive metrics and entities.
        
        :param articles: List of article dictionaries
        :param table_name: Name of the BigQuery table
        :return: Processed DataFrame or None
        """
        if not articles:
            logging.warning("No articles to write to BigQuery.")
            return None
        
        try:
            # Convert articles to DataFrame
            df = pd.DataFrame(articles)
            
            # Add timestamp column
            df['scrape_timestamp'] = datetime.now()
            
            # Post-processing metrics
            df['title_word_count'] = df['title'].apply(self._count_words)
            df['title_char_count'] = df['title'].apply(len)
            
            # Capitalized words processing
            df['capitalized_words'] = df['title'].apply(self._find_capitalized_words)
            
            # Ensure entity columns exist
            entity_columns = ['persons', 'organizations', 'locations']
            for col in entity_columns:
                if col not in df.columns:
                    df[col] = [[] for _ in range(len(df))]
            
            # Convert entity lists to comma-separated strings for BigQuery
            for col in entity_columns:
                df[col] = df[col].apply(lambda x: ','.join(x) if isinstance(x, list) else str(x))
            
            # Define schema for BigQuery
            schema = [
                {'name': 'title', 'type': 'STRING'},
                {'name': 'kicker', 'type': 'STRING'},
                {'name': 'link', 'type': 'STRING'},
                {'name': 'image', 'type': 'STRING'},
                {'name': 'date', 'type': 'STRING'},
                {'name': 'scrape_timestamp', 'type': 'TIMESTAMP'},
                {'name': 'title_word_count', 'type': 'INTEGER'},
                {'name': 'title_char_count', 'type': 'INTEGER'},
                {'name': 'capitalized_words', 'type': 'STRING'},
                {'name': 'persons', 'type': 'STRING'},
                {'name': 'organizations', 'type': 'STRING'},
                {'name': 'locations', 'type': 'STRING'}
            ]
            
            # Full table name
            full_table_name = f'{self.dataset}.{table_name}'
            
            logging.info(f"Writing {len(df)} articles to BigQuery table {full_table_name}")
            
            # Write to BigQuery
            pandas_gbq.to_gbq(
                df,
                full_table_name,
                project_id=self.project_id,
                table_schema=schema,
                if_exists='append'
            )
            
            logging.info(f"Successfully wrote {len(df)} articles to {full_table_name}")
            
            # Log summary
            self._log_article_summary(df)
            
            return df
        
        except Exception as e:
            logging.error(f"Error writing to BigQuery: {e}")
            return None
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        try:
            return len(str(text).split())
        except Exception as e:
            logging.warning(f"Error counting words: {e}")
            return 0
    
    def _find_capitalized_words(self, text: str) -> str:
        """Find capitalized words."""
        import re
        try:
            return ','.join(re.findall(r'\b[A-Z][a-z]*\b', str(text)))
        except Exception as e:
            logging.warning(f"Error finding capitalized words: {e}")
            return ''
    
    def _log_article_summary(self, df: pd.DataFrame):
        """Log summary of processed articles."""
        try:
            logging.info("Article Processing Summary:")
            logging.info(f"Total Articles: {len(df)}")
            logging.info(f"Avg Title Word Count: {df['title_word_count'].mean():.2f}")
            logging.info(f"Avg Title Character Count: {df['title_char_count'].mean():.2f}")
            
            # Entity summary
            entity_columns = ['persons', 'organizations', 'locations']
            for col in entity_columns:
                entities = [e for entities in df[col] for e in str(entities).split(',') if e.strip()]
                top_entities = pd.Series(entities).value_counts().head(5)
                
                logging.info(f"\nTop {col.capitalize()}:")
                for entity, count in top_entities.items():
                    logging.info(f"  {entity}: {count}")
        
        except Exception as e:
            logging.error(f"Error generating article summary: {e}")