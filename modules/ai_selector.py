#!/usr/bin/env python3
"""
AI-based selector for finding the correct DOM elements.
"""
import logging
import os
import re
import json
from bs4 import BeautifulSoup
from openai import OpenAI

logger = logging.getLogger(__name__)

class AiSelector:
    """Class for using AI to identify correct DOM selectors."""
    
    def __init__(self):
        """Initialize the AI selector."""
        # Try to load API key from environment
        try:
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

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
        
        If OpenAI API key is not available, returns default selectors.
        Otherwise, uses AI to predict selectors.
        """
        # Check if client is initialized
        if not self.client:
            logger.warning("OpenAI client not initialized. Using default selectors.")
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
                model="o3-mini",
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
                        
                        Respond with a valid JSON object with these keys: article_container, title, kicker, link, image
                        
                        Here is the HTML sample:
                        {sample_article}
                        """
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                selectors = json.loads(ai_response)
                logger.info("Successfully generated selectors using AI")
                return selectors
            except json.JSONDecodeError:
                logger.warning("Could not parse AI response. Using default selectors.")
                return self.default_selectors
                
        except Exception as e:
            logger.error(f"Error using AI to get selectors: {e}")
            return self.default_selectors