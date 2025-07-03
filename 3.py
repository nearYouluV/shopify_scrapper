import requests
from bs4 import BeautifulSoup
from reviews import scrape_reviews
from logger import logger
from scrape_apps import fetch_sitemap
from threading import Thread
# def get_app_ids():
#     for page in range(1,37):
#         url = f"{BASE_URL}?page={page}"
#         response = requests.get(url)
#         if response.status_code != 200:
#             logger.error(f"Failed to fetch page {page}, trying again...")
#             while response.status_code != 200:

#                 response = requests.get(url)
#                 if response.status_code == 404:
#                     break
#         logger.info(f"Fetching page {page}")
#         soup = BeautifulSoup(response.text, 'html.parser')
#         app_links = soup.find_all("div", attrs={"data-controller": "app-card"})
#         for link in app_links:
#             app_id = link.find('a').get('href').split('/')[-1].split('?')[0]
#             scrape_reviews(app_id)
#             logger.info(f"Scraped reviews for app ID: {app_id}")

def scrape_app_reviews(app_ids=[]):
    print(urls[:10])
    for app in app_ids:
        scrape_reviews(app)
        logger.info(f"Scraped reviews for app ID: {app}")

if __name__ == "__main__":
    urls = fetch_sitemap()
    [url.split('/')[-1].split('?')[0] for url in urls if 'partners' not in url]
    num_threads = 4
    threads = []
    batch_size = len(urls) // num_threads
    for i in range(num_threads):
        start_index = i * batch_size
        end_index = start_index + batch_size if i < num_threads - 1 else len(urls)
        thread = Thread(target=scrape_app_reviews, args=(urls[start_index:end_index],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    logger.info("Finished scraping all app reviews.")