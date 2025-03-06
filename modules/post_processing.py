#!/usr/bin/env python3
"""
Post-processing module for Yogonet International scraper.
Adds additional metrics and analysis to scraped articles.
"""

import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ArticlePostProcessor:
    """
    Handles post-processing of scraped articles with additional metrics.
    """

    @staticmethod
    def process_articles(articles):
        """
        Process the scraped articles and add additional metrics.
        
        :param articles: List of dictionaries containing article information
        :return: Pandas DataFrame with original and additional metrics
        """
        # Convert to DataFrame
        df = pd.DataFrame(articles)
        
        # Add post-processing metrics
        df['title_word_count'] = df['title'].apply(ArticlePostProcessor._count_words)
        df['title_char_count'] = df['title'].apply(len)
        df['capitalized_words'] = df['title'].apply(ArticlePostProcessor._find_capitalized_words)
        
        # Additional optional metrics can be added here
        df['title_complexity_score'] = df['title'].apply(ArticlePostProcessor._calculate_complexity_score)
        
        return df
    
    @staticmethod
    def _count_words(text):
        """
        Count the number of words in the given text.
        
        :param text: Input text
        :return: Number of words
        """
        try:
            return len(text.split())
        except Exception as e:
            logger.warning(f"Error counting words in text '{text}': {e}")
            return 0
    
    @staticmethod
    def _find_capitalized_words(text):
        """
        Find words that start with a capital letter.
        
        :param text: Input text
        :return: List of capitalized words
        """
        try:
            # Use regex to find words starting with a capital letter
            return re.findall(r'\b[A-Z][a-z]*\b', text)
        except Exception as e:
            logger.warning(f"Error finding capitalized words in text '{text}': {e}")
            return []
    
    @staticmethod
    def _calculate_complexity_score(text):
        """
        Calculate a simple complexity score based on title characteristics.
        
        :param text: Input text
        :return: Complexity score
        """
        try:
            # Complexity based on:
            # - Number of words
            # - Number of capitalized words
            # - Presence of special characters
            word_count = len(text.split())
            capitalized_count = len(re.findall(r'\b[A-Z][a-z]*\b', text))
            special_chars = len(re.findall(r'[^\w\s]', text))
            
            # Simple scoring mechanism
            complexity = (word_count * 0.5) + (capitalized_count * 1.5) + (special_chars * 2)
            return round(complexity, 2)
        except Exception as e:
            logger.warning(f"Error calculating complexity for text '{text}': {e}")
            return 0
    
    @staticmethod
    def generate_summary_report(df):
        """
        Generate a summary report of the processed articles.
        
        :param df: Processed DataFrame
        :return: Dictionary with summary statistics
        """
        try:
            summary = {
                'total_articles': len(df),
                'avg_title_word_count': df['title_word_count'].mean(),
                'avg_title_char_count': df['title_char_count'].mean(),
                'most_common_capitalized_words': df['capitalized_words']
                    .apply(pd.Series)
                    .stack()
                    .value_counts()
                    .head(10)
                    .to_dict(),
                'max_title_complexity': df['title_complexity_score'].max(),
                'min_title_complexity': df['title_complexity_score'].min(),
                'avg_title_complexity': df['title_complexity_score'].mean()
            }
            return summary
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return {}

# Example usage
def main():
    # Sample articles for testing
    sample_articles = [
        {'title': 'Breaking News: Tech Giant Launches New Product', 'link': 'example.com/1'},
        {'title': 'Local Government Announces Budget Cuts', 'link': 'example.com/2'}
    ]
    
    # Process articles
    processor = ArticlePostProcessor()
    df = processor.process_articles(sample_articles)
    
    # Generate summary
    summary = processor.generate_summary_report(df)
    
    # Print results
    print("Processed DataFrame:")
    print(df)
    print("\nSummary Report:")
    print(summary)

if __name__ == "__main__":
    main()