#!/usr/bin/env python3
"""
AI-based selector for finding the correct DOM elements.
"""
import logging
import os
import re
import json
from bs4 import BeautifulSoup
import openai

logger = logging.getLogger(__name__)

class AiSelector:
    """Class for using AI to identify correct DOM selectors."""
    
    def __init__(self):
        """Initialize the AI selector."""
        # Try to load API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
        self.default_selectors = {
            'article_container': '.slot.noticia',
            'title': '.titulo a',
            'kicker': '.volanta',
            'link': '.titulo a',
            'image': '.imagen a img'
        }
    
    def get_selectors(self, html):
        """
        Get the selectors for the articles on the page.
        
        If OpenAI API key is not available, returns default selectors.
        Otherwise, uses AI to predict selectors.
        """
        if not openai.api_key:
            logger.warning("OpenAI API key not found. Using default selectors.")
            return self.default_selectors
        
        try:
            # Extract a sample of the HTML to analyze
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find a sample article to send to the AI
            sample_article = soup.select_one('.slot.noticia')
            
            if not sample_article:
                logger.warning("No sample article found. Using default selectors.")
                return self.default_selectors
            
            # Send a request to the OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a web scraping assistant. Your task is to analyze HTML and identify CSS selectors for news articles."},
                    {"role": "user", "content": f"""
                    Based on this HTML sample of a news article from Yogonet International, please identify the CSS selectors for:
                    1. The container element for each article
                    2. The title element
                    3. The kicker/subtitle element
                    4. The link element to the full article
                    5. The image element
                    
                    Respond with a valid JSON object with these keys: article_container, title, kicker, link, image
                    
                    Here is the HTML sample:
                    {sample_article}
                    """}
                ]
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content
            
            # Extract the JSON part
            json_match = re.search(r'{.*}', ai_response, re.DOTALL)
            if json_match:
                selectors = json.loads(json_match.group(0))
                logger.info("Successfully generated selectors using AI")
                return selectors
            else:
                logger.warning("Could not parse AI response. Using default selectors.")
                return self.default_selectors
                
        except Exception as e:
            logger.error(f"Error using AI to get selectors: {e}")
            return self.default_selectors