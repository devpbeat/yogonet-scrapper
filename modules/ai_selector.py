#!/usr/bin/env python3
"""
AI-based selector for finding the correct DOM elements.
"""
import logging
import os
import json
from bs4 import BeautifulSoup
from openai import OpenAI

logger = logging.getLogger(__name__)

class AiSelector:
    """Class for using AI to identify correct DOM selectors."""
    
    def __init__(self):
        """Initialize the AI selector."""
        # Hardcoded API key for testing
        
        # Alternative methods to get API key (uncomment if needed)
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Default selectors
        self.default_selectors = {
            'article_container': '.contenedor_dato_modulo',
            'title': '.titulo',
            'kicker': '.volanta',
            'link': 'a',
            'image': 'img'
        }
    
    def get_selectors(self, html):
        """
        Get the selectors for the articles on the page.
        
        :param html: HTML content to analyze
        :return: Dictionary of CSS selectors
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find a sample article
            sample_article = soup.select_one('.contenedor_dato_modulo')
            
            if not sample_article:
                logger.warning("No sample article found. Using default selectors.")
                return self.default_selectors
            
            # Create AI request without JSON schema (simpler approach)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a web scraping expert specializing in identifying precise CSS selectors for news article elements."
                    },
                    {
                        "role": "user", 
                        "content": f"""
                        Analyze this HTML snippet from a Yogonet International news page and extract the most precise CSS selectors:

                        {sample_article}

                        Respond with a JSON object containing these EXACT keys:
                        - article_container
                        - title
                        - kicker
                        - link
                        - image

                        Example format:
                        {{
                            "article_container": ".contenedor_dato_modulo",
                            "title": ".titulo",
                            "kicker": ".volanta",
                            "link": "a",
                            "image": "img"
                        }}

                        Focus on:
                        - Minimal, precise selectors
                        - Selectors that work across multiple articles
                        - Prioritizing class and ID selectors
                        """
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.7
            )
            
            # Extract and parse the response
            try:
                # Parse the JSON response
                selectors = json.loads(response.choices[0].message.content)
                
                # Validate selectors
                for key in ['article_container', 'title', 'kicker', 'link', 'image']:
                    if not selectors.get(key):
                        logger.warning(f"Missing selector for {key}")
                        return self.default_selectors
                
                logger.info("Successfully generated selectors using AI")
                return selectors
            
            except (json.JSONDecodeError, TypeError) as parse_error:
                logger.error(f"Failed to parse AI response: {parse_error}")
                return self.default_selectors
        
        except Exception as e:
            logger.error(f"Unexpected error in AI selector: {e}")
            return self.default_selectors