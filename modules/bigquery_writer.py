#!/usr/bin/env python3
"""
Module for writing scraped data to BigQuery using direct BigQuery client.
"""
import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from google.cloud import bigquery

class BigQueryWriter:
    """Class for writing data to BigQuery using the BigQuery client library."""
    
    def __init__(self):
        """Initialize the BigQuery writer."""
        self.dataset = os.environ.get('DATASET', 'yogonet')
        self.project_id = os.environ.get('PROJECT_ID')
        
        if not self.project_id:
            logging.warning("PROJECT_ID environment variable not set. Using default project.")
        
        try:
            # Initialize BigQuery client
            self.client = bigquery.Client()
            logging.info(f"BigQuery client initialized for project: {self.project_id}")
        except Exception as e:
            logging.error(f"Failed to initialize BigQuery client: {e}")
            self.client = None
    
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
        
        if not self.client:
            logging.error("BigQuery client not initialized. Cannot write to BigQuery.")
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
                bigquery.SchemaField("title", "STRING"),
                bigquery.SchemaField("kicker", "STRING"),
                bigquery.SchemaField("link", "STRING"),
                bigquery.SchemaField("image", "STRING"),
                bigquery.SchemaField("date", "STRING"),
                bigquery.SchemaField("scrape_timestamp", "TIMESTAMP"),
                bigquery.SchemaField("title_word_count", "INTEGER"),
                bigquery.SchemaField("title_char_count", "INTEGER"),
                bigquery.SchemaField("capitalized_words", "STRING"),
                bigquery.SchemaField("persons", "STRING"),
                bigquery.SchemaField("organizations", "STRING"),
                bigquery.SchemaField("locations", "STRING")
            ]
            
            # Full table name
            full_table_id = f"{self.project_id}.{self.dataset}.{table_name}"
            
            logging.info(f"Writing {len(df)} articles to BigQuery table {full_table_id}")
            
            # Configure job
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            # Write to BigQuery using direct client load
            try:
                job = self.client.load_table_from_dataframe(
                    df, full_table_id, job_config=job_config
                )
                
                # Wait for the job to complete
                job.result()
                
                logging.info(f"Successfully wrote {len(df)} articles to {full_table_id}")
                
                # Log summary
                self._log_article_summary(df)
                
                return df
            except Exception as job_error:
                logging.error(f"BigQuery load job failed: {job_error}")
                return None
        
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