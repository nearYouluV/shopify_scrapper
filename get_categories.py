import requests
from bs4 import BeautifulSoup
from models import Session
from threading import Thread
from time import sleep
import tls_client
from fake_useragent import UserAgent
# from models import Category, Subcategory, Tag

ua = UserAgent()
# headers=

base_url = "https://apps.shopify.com/categories/"

import requests

cookies = {
    "shopify_experiment_assignments": "%5B%5D",
    "_shopify_dev_session": "rGuPW1qG8DKUeEV3fC7hFbMK%2B6GL%2BKpu0ER3VeDp4%2FWHI6qVkWI957jN9h5YSci8hoX1JjN9Uz873qGPsayrfZyfdFGntjQJPaKswQMYklWbLfNzKTFOPS3aZ9F%2BXWfeYBZs0FMosqgJLX6WHRbDGlcTCOoGqsYqTXVt9lfvj3vQhcUc3gtVUCCsQDSO05EqDD8oLbjzVzlOg8XGJSMzxQxgvWL0ku4HL8WGYOWPupNzhuur6XXUdsjN%2BpD%2BG4J%2BhJ7TCbuRynVGozEOz3q3qCwDkiF8w6O1yuDHTA%3D%3D--m6d9jvG76Jd8BJ3p--dpihL%2BtnblaWdL53NK2%2FBw%3D%3D",
    "theme_mode": "ThemeMode-dark",
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru,en-US;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "if-none-match": 'W/"1dbdff14640b59515f638a06f0ad94cb"',
    "priority": "u=0, i",
    "referer": "https://www.upwork.com/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    # 'cookie': 'shopify_experiment_assignments=%5B%5D; _shopify_dev_session=rGuPW1qG8DKUeEV3fC7hFbMK%2B6GL%2BKpu0ER3VeDp4%2FWHI6qVkWI957jN9h5YSci8hoX1JjN9Uz873qGPsayrfZyfdFGntjQJPaKswQMYklWbLfNzKTFOPS3aZ9F%2BXWfeYBZs0FMosqgJLX6WHRbDGlcTCOoGqsYqTXVt9lfvj3vQhcUc3gtVUCCsQDSO05EqDD8oLbjzVzlOg8XGJSMzxQxgvWL0ku4HL8WGYOWPupNzhuur6XXUdsjN%2BpD%2BG4J%2BhJ7TCbuRynVGozEOz3q3qCwDkiF8w6O1yuDHTA%3D%3D--m6d9jvG76Jd8BJ3p--dpihL%2BtnblaWdL53NK2%2FBw%3D%3D; theme_mode=ThemeMode-dark',
}


def get_categories_name():
    response = requests.get(
        "https://shopify.dev/docs/apps/launch/app-store-review/app-listing-categories#sales-channels",
    )
    print(response.url)
    soup = BeautifulSoup(response.text, "lxml")
    for col in soup.find("table").find_all("tr")[1:]:
        if len(col.find_all("td")) == 3:
            category_name = col.find("td").find("strong").text.strip()
            subcategory_name = col.find_all("td")[1].find("strong").text.strip()
            tag_name = col.find_all("td")[2].find("strong").text.strip()
            with Session() as session:
                session.add(
                    Category(
                        name=category_name, id=category_name.lower().replace(" ", "-")
                    )
                )
                session.add(
                    Subcategory(
                        name=subcategory_name,
                        id=subcategory_name.lower().replace(" ", "-"),
                        category_id=category_name.lower().replace(" ", "-"),
                    )
                )  # want to add category id to relate
                session.add(
                    Tag(
                        name=tag_name,
                        id=tag_name.lower().replace(" ", "-"),
                        subcategory_id=subcategory_name.lower().replace(" ", "-"),
                    )
                )  # want to add subcategory_id to relate
                session.commit()
        if len(col.find_all("td")) == 2:
            subcategory_name = col.find_all("td")[0].find("strong").text.strip()
            tag_name = col.find_all("td")[1].find("strong").text.strip()
            with Session() as session:
                session.add(
                    Subcategory(
                        name=subcategory_name,
                        id=subcategory_name.lower().replace(" ", "-"),
                        category_id=category_name.lower().replace(" ", "-"),
                    )
                )  # want to add category id to relate
                session.add(
                    Tag(
                        name=tag_name,
                        id=tag_name.lower().replace(" ", "-"),
                        subcategory_id=subcategory_name.lower().replace(" ", "-"),
                    )
                )  # want to add subcategory_id to relate
                session.commit()
        if len(col.find_all("td")) == 1:
            tag_name = col.find_all("td")[0].find("strong").text.strip()
            with Session() as session:
                session.add(
                    Tag(
                        name=tag_name,
                        id=tag_name.lower().replace(" ", "-"),
                        subcategory_id=subcategory_name.lower().replace(" ", "-"),
                    )
                )  # want to add subcategory_id to relate
                session.commit()


if __name__ == "__main__":
    get_categories_name()
