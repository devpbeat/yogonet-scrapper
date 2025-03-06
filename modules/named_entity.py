#!/usr/bin/env python3
"""
Named Entity Extraction Module for Scraped Articles
"""

import logging
import spacy
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class NamedEntityExtractor:
    """
    Extracts named entities from text using spaCy.
    Supports extraction of persons, organizations, and locations.
    """
    
    def __init__(self, model: str = 'en_core_web_sm'):
        """
        Initialize the Named Entity Extractor.
        
        :param model: spaCy language model to use
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            logger.warning(f"Model {model} not found. Downloading...")
            spacy.cli.download(model)
            self.nlp = spacy.load(model)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the given text.
        
        :param text: Input text to extract entities from
        :return: Dictionary of extracted entities
        """
        if not text:
            return {
                'persons': [],
                'organizations': [],
                'locations': []
            }
        
        try:
            doc = self.nlp(text)
            
            # Extract entities
            entities = {
                'persons': [],
                'organizations': [],
                'locations': []
            }
            
            for ent in doc.ents:
                # Normalize entity type mapping
                if ent.label_ in ['PERSON', 'PERSONAGE']:
                    entities['persons'].append(ent.text)
                elif ent.label_ in ['ORG', 'ORGANIZATION']:
                    entities['organizations'].append(ent.text)
                elif ent.label_ in ['LOC', 'GPE', 'LOCATION']:
                    entities['locations'].append(ent.text)
            
            # Remove duplicates while preserving order
            for key in entities:
                entities[key] = list(dict.fromkeys(entities[key]))
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                'persons': [],
                'organizations': [],
                'locations': []
            }
    
    def extract_entities_from_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Extract entities from multiple articles.
        
        :param articles: List of article dictionaries
        :return: List of articles with added entity information
        """
        for article in articles:
            # Try extracting from title and kicker
            text_to_analyze = f"{article.get('title', '')} {article.get('kicker', '')}"
            
            try:
                entities = self.extract_entities(text_to_analyze)
                
                # Add entities to the article
                article['persons'] = entities['persons']
                article['organizations'] = entities['organizations']
                article['locations'] = entities['locations']
            
            except Exception as e:
                logger.warning(f"Could not extract entities for article: {e}")
                article['persons'] = []
                article['organizations'] = []
                article['locations'] = []
        
        return articles

def main():
    """
    Example usage of Named Entity Extractor
    """
    extractor = NamedEntityExtractor()
    
    # Sample articles
    sample_articles = [
        {
            'title': 'Google Announces New AI Features at Conference in San Francisco',
            'kicker': 'Tech Giant Expands Machine Learning Capabilities'
        },
        {
            'title': 'Elon Musk Launches New SpaceX Mission to Mars',
            'kicker': 'Private Space Exploration Continues to Advance'
        }
    ]
    
    # Extract entities
    processed_articles = extractor.extract_entities_from_articles(sample_articles)
    
    # Print results
    print(json.dumps(processed_articles, indent=2))

if __name__ == "__main__":
    main()