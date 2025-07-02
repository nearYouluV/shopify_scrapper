import requests
from bs4 import BeautifulSoup
from reviews import scrape_reviews
from logger import logger
BASE_URL = 'https://apps.shopify.com/categories/store-management-operations-analytics/all'
def get_app_ids():
    for page in range(1,37):
        url = f"{BASE_URL}?page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch page {page}, trying again...")
            while response.status_code != 200:

                response = requests.get(url)
                if response.status_code == 404:
                    break
        logger.info(f"Fetching page {page}")
        soup = BeautifulSoup(response.text, 'html.parser')
        app_links = soup.find_all("div", attrs={"data-controller": "app-card"})
        for link in app_links:
            app_id = link.find('a').get('href').split('/')[-1].split('?')[0]
            scrape_reviews(app_id)
            logger.info(f"Scraped reviews for app ID: {app_id}")

if __name__ == "__main__":
    get_app_ids()
    logger.info("Finished scraping all app reviews.")