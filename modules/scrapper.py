#!/usr/bin/env python3
"""
Yogonet International Web Scraper Module
Extracts latest news articles from the website.
"""

import logging
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_binary
from .ai_selector import AiSelector

# Configure logging
logger = logging.getLogger(__name__)

class YogonetScraper:
    """
    A comprehensive scraper for Yogonet International website.
    Handles scraping of articles and website content.
    """

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper with configurable browser options.
        
        :param headless: Whether to run the browser in headless mode
        """
        self.base_url = "https://www.yogonet.com/international/"
        self.driver = None
        self.headless = headless
        self.ai_selector = AiSelector()
        
    def _setup_driver(self) -> webdriver.Chrome:
        """
        Set up and configure Chrome WebDriver.
        
        :return: Configured Chrome WebDriver
        """
        chrome_options = Options()
        
        # Headless configuration
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Performance and compatibility options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        try:
            # Use WebDriverManager to handle driver installation
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def scrape_articles(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Scrape articles from Yogonet International homepage.
        
        :param limit: Optional limit on number of articles to scrape
        :return: List of dictionaries containing article information
        """
        try:
            # Use requests to fetch the page content
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Use AI Selector to get dynamic selectors
            try:
                selectors = self.ai_selector.get_selectors(response.text)
            except Exception as selector_error:
                logger.warning(f"AI Selector failed, using fallback selectors: {selector_error}")
                selectors = {
                    'article_container': '.contenedor_dato_modulo',
                    'title': '.titulo',
                    'kicker': '.volanta',
                    'link': 'a',
                    'image': 'img'
                }
            
            # Find article containers using dynamic selectors
            article_containers = soup.select(selectors.get('article_container', '.contenedor_dato_modulo'))
            
            articles = []
            for container in article_containers[:limit]:
                try:
                    # Extract article details using dynamic selectors
                    title_elem = container.select_one(selectors.get('title', '.titulo'))
                    kicker_elem = container.select_one(selectors.get('kicker', '.volanta'))
                    link_elem = container.select_one(selectors.get('link', 'a'))
                    image_elem = container.select_one(selectors.get('image', 'img'))
                    
                    if title_elem and link_elem:
                        article = {
                            'title': title_elem.text.strip(),
                            'kicker': kicker_elem.text.strip() if kicker_elem else 'No kicker',
                            'link': link_elem.get('href', ''),
                            'image': image_elem.get('src', '') if image_elem else '',
                            'date': container.find('div', class_='fecha_actual').text.strip() if container.find('div', class_='fecha_actual') else 'No date'
                        }
                        
                        # Ensure absolute URL
                        if article['link'] and article['link'].startswith('/'):
                            article['link'] = f"https://www.yogonet.com{article['link']}"
                        
                        # Ensure absolute image URL
                        if article['image'] and article['image'].startswith('/'):
                            article['image'] = f"https://www.yogonet.com{article['image']}"
                        
                        articles.append(article)
                
                except Exception as article_error:
                    logger.warning(f"Error processing article: {article_error}")
            
            logger.info(f"Scraped {len(articles)} articles")
            return articles
        
        except requests.RequestException as req_error:
            logger.error(f"Request error: {req_error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in scraping: {e}")
            return []

    def close(self):
        """
        Properly close the WebDriver if it exists.
        """
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")