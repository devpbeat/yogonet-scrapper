#!/usr/bin/env python3
"""
Module for writing scraped data to BigQuery via local JSON file.
"""
import os
import json
import logging
import tempfile
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class BigQueryWriter:
    """Class for writing data to BigQuery using local file approach."""
    
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
        Write articles to BigQuery table using local file approach.
        
        :param articles: List of article dictionaries
        :param table_name: Name of the BigQuery table
        :return: Processed DataFrame or None
        """
        if not articles:
            logging.warning("No articles to write to BigQuery.")
            return None
        
        try:
            # Convert articles to DataFrame for processing
            df = pd.DataFrame(articles)
            
            # Add timestamp column
            df['scrape_timestamp'] = datetime.now().isoformat()
            
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
            
            # Convert entity lists to comma-separated strings
            for col in entity_columns:
                df[col] = df[col].apply(lambda x: ','.join(x) if isinstance(x, list) else str(x))
            
            # Convert the DataFrame back to a list of dictionaries
            processed_articles = df.to_dict(orient='records')
            
            # Write to temporary JSONL file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
                for article in processed_articles:
                    # Convert any non-serializable objects to strings
                    article_serializable = {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                                         for k, v in article.items()}
                    json.dump(article_serializable, f)
                    f.write('\n')  # Add newline for JSONL format
                
                temp_file_path = f.name
            
            logging.info(f"Wrote {len(processed_articles)} articles to temp file: {temp_file_path}")
            
            # Now load the JSON file into BigQuery
            success = self._load_json_to_bigquery(temp_file_path, table_name, df)
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                logging.info(f"Deleted temporary file: {temp_file_path}")
            except Exception as e:
                logging.warning(f"Failed to delete temporary file: {e}")
            
            return df if success else None
            
        except Exception as e:
            logging.error(f"Error preparing data for BigQuery: {e}", exc_info=True)
            return None
    
    def _load_json_to_bigquery(self, json_file_path, table_name, df):
        """Load JSON file into BigQuery."""
        try:
            # Initialize BigQuery client
            logging.info("Initializing BigQuery client...")
            client = bigquery.Client()
            
            # Define table reference
            full_table_id = f"{self.project_id}.{self.dataset}.{table_name}"
            logging.info(f"Target table: {full_table_id}")
            
            # Check if dataset exists, create if not
            try:
                client.get_dataset(f"{self.project_id}.{self.dataset}")
                logging.info(f"Dataset {self.dataset} exists")
            except Exception as e:
                logging.info(f"Dataset {self.dataset} not found, creating... Error: {e}")
                dataset = bigquery.Dataset(f"{self.project_id}.{self.dataset}")
                dataset.location = "US"
                client.create_dataset(dataset)
                logging.info(f"Dataset {self.dataset} created")
            
            # Configure job
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                autodetect=True,  # Let BigQuery detect the schema
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            logging.info(f"Loading data from {json_file_path} to {full_table_id}...")
            
            # Load data from file
            with open(json_file_path, "rb") as source_file:
                job = client.load_table_from_file(
                    source_file,
                    full_table_id,
                    job_config=job_config
                )
            
            # Wait for the job to complete
            job.result()
            
            logging.info(f"Loaded {job.output_rows} rows into {full_table_id}")
            
            # Log summary
            self._log_article_summary(df)
            
            return True
            
        except Exception as e:
            logging.error(f"Error loading JSON to BigQuery: {e}", exc_info=True)
            import traceback
            logging.error(traceback.format_exc())
            return False
    
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