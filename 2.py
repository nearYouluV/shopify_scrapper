from main import scrape_app_page
import requests
from bs4 import BeautifulSoup
from logger import logger
BASE_URL = "https://apps.shopify.com/sitemap.xml"

def fetch_sitemap():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        soup  = BeautifulSoup(response.content, 'xml')
        urls = [loc.text for loc in soup.find_all('loc')]
        return urls
    return None

def main():
    urls = fetch_sitemap()
    if urls:
        for url in urls:
            if "apps.shopify.com" in url:
                logger.info(f"Processing URL: {url}")
                scrape_app_page(url)

    else:
        logger.error("Failed to fetch sitemap.")
if __name__ == "__main__":
    main()