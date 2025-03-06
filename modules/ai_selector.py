#!/usr/bin/env python3
"""
AI-based selector for finding the correct DOM elements.
"""
import logging
import os
import re
import json
from bs4 import BeautifulSoup

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class AiSelector:
    """Class for using AI to identify correct DOM selectors."""
    
    def __init__(self):
        """Initialize the AI selector."""
        # Default selectors in case AI fails
        self.default_selectors = {
            'article_container': '.contenedor_dato_modulo',
            'title': '.titulo',
            'kicker': '.volanta',
            'link': 'a',
            'image': 'img'
        }
        
        # Try to initialize OpenAI client
        self.client = None
        self._initialize_openai_client()
    
    def _initialize_openai_client(self):
        """
        Initialize OpenAI client with robust error handling.
        """
        if not OpenAI:
            logger.warning("OpenAI library not installed. AI selectors disabled.")
            return
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        if not api_key:
            logger.warning("No OpenAI API key found. AI selectors disabled.")
            return
        
        try:
            self.client = OpenAI(api_key=api_key)
            
            # Verify the key works with a simple test
            self.client.models.list(limit=1)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def get_selectors(self, html):
        """
        Get the selectors for the articles on the page.
        
        Fallback to default selectors if AI fails.
        """
        # If no client, return default selectors
        if not self.client:
            logger.warning("OpenAI client not available. Using default selectors.")
            return self.default_selectors
        
        try:
            # Extract a sample of the HTML to analyze
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find a sample article to send to the AI
            sample_article = soup.select_one('.contenedor_dato_modulo')
            
            if not sample_article:
                logger.warning("No sample article found. Using default selectors.")
                return self.default_selectors
            
            # Send a request to the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a web scraping assistant. Your task is to analyze HTML and identify CSS selectors for news articles."
                    },
                    {
                        "role": "user", 
                        "content": f"""
                        Based on this HTML sample of a news article from Yogonet International, please identify the CSS selectors for:
                        1. The container element for each article
                        2. The title element
                        3. The kicker/subtitle element
                        4. The link element to the full article
                        5. The image element
                        
                        Respond ONLY with a valid JSON object with these keys: article_container, title, kicker, link, image
                        
                        Example format:
                        {{
                            "article_container": ".contenedor_dato_modulo",
                            "title": ".titulo",
                            "kicker": ".volanta",
                            "link": "a",
                            "image": "img"
                        }}
                        
                        Here is the HTML sample:
                        {sample_article}
                        """
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                selectors = json.loads(ai_response)
                
                # Validate the selectors
                for key in ['article_container', 'title', 'kicker', 'link', 'image']:
                    if key not in selectors or not isinstance(selectors[key], str):
                        raise ValueError(f"Missing or invalid selector for {key}")
                
                logger.info("Successfully generated selectors using AI")
                return selectors
            except (json.JSONDecodeError, ValueError) as parse_error:
                logger.warning(f"Could not parse AI response: {parse_error}. Using default selectors.")
                return self.default_selectors
                
        except Exception as e:
            logger.error(f"Error using AI to get selectors: {e}")
            return self.default_selectors