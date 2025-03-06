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
        self.dataset = os.environ.get('DATASET')
        if not self.dataset:
            logger.warning("DATASET environment variable not set. Using 'yogonet' as default.")
            self.dataset = 'yogonet'
        
        self.project_id = os.environ.get('PROJECT_ID')
        if not self.project_id:
            logger.warning("PROJECT_ID environment variable not set. Using default project.")
    
    def write_articles(self, articles, table_name='articles'):
        """
        Write articles to BigQuery table.
        
        Args:
            articles: List of article dictionaries with title, kicker, link, and image
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
            
            # Define schema
            schema = [
                {'name': 'title', 'type': 'STRING'},
                {'name': 'kicker', 'type': 'STRING'},
                {'name': 'link', 'type': 'STRING'},
                {'name': 'image', 'type': 'STRING'},
                {'name': 'scrape_timestamp', 'type': 'TIMESTAMP'}
            ]
            
            # Full table name
            full_table_name = f'{self.dataset}.{table_name}'
            
            logger.info(f"Writing {len(df)} articles to BigQuery table {full_table_name}")
            
            # Write to BigQuery
            pandas_gbq.to_gbq(
                df,
                full_table_name,
                project_id=self.project_id,
                table_schema=schema,
                if_exists='append'
            )
            
            logger.info(f"Successfully wrote {len(df)} articles to {full_table_name}")
            
        except Exception as e:
            logger.error(f"Error writing to BigQuery: {e}")