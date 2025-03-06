#!/usr/bin/env python3
"""
Yogonet scraper implementation using Selenium and AI-based element selection.
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from ai_selector import AiSelector

logger = logging.getLogger(__name__)

class YogonetScraper:
    """Class for scraping Yogonet International website."""
    
    def __init__(self):
        """Initialize the scraper with a headless Chrome browser."""
        self.url = "https://www.yogonet.com/international/"
        self.driver = self._setup_driver()
        self.ai_selector = AiSelector()
        
    def _setup_driver(self):
        """Set up and return a headless Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    
    def scrape_articles(self):
        """Scrape articles from Yogonet International."""
        logger.info(f"Navigating to {self.url}")
        self.driver.get(self.url)
        
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        
        logger.info("Page loaded, analyzing content")
        
        # Get the page source and parse it with BeautifulSoup
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Use AI to find article selectors
        selectors = self.ai_selector.get_selectors(html)
        
        logger.info(f"Using selectors: {selectors}")
        
        # Find all articles using the selectors
        articles = []
        
        # Find all article elements
        article_elements = soup.select(selectors['article_container'])
        
        for article_elem in article_elements:
            try:
                # Extract article data
                title_elem = article_elem.select_one(selectors['title'])
                kicker_elem = article_elem.select_one(selectors['kicker'])
                link_elem = article_elem.select_one(selectors['link'])
                image_elem = article_elem.select_one(selectors['image'])
                
                # Extract text/attributes
                title = title_elem.text.strip() if title_elem else "No title found"
                kicker = kicker_elem.text.strip() if kicker_elem else "No kicker found"
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "No link found"
                image = image_elem['src'] if image_elem and 'src' in image_elem.attrs else "No image found"
                
                # Ensure the link is absolute
                if link.startswith("/"):
                    link = f"https://www.yogonet.com{link}"
                
                articles.append({
                    'title': title,
                    'kicker': kicker,
                    'link': link,
                    'image': image
                })
            except Exception as e:
                logger.error(f"Error extracting article data: {e}")
        
        return articles
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()