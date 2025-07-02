import requests
from bs4 import BeautifulSoup
from time import sleep
from models import *
from sqlalchemy import select
from datetime import datetime
from logger import logger

BASE_URL = "https://apps.shopify.com/"


def scrape_reviews(app_id):
    scraped_ids = []
    reviews = []
    page = 1
    sort = 'relevance'
    while True:

        url = f"{BASE_URL}{app_id}/reviews?page={page}&sort_by={sort}"
        logger.info(f"Scraping reviews for app ID: {app_id}, page: {page}, sort: {sort}")
        r = requests.get(
            url,
        )
        if r.status_code == 404:
            if items_count > 10_000 and sort == 'relevance':
                page = 1
                sort = 'newest'
            else:
                load_reviews(reviews)
                return
        if r.status_code != 200:
            while r.status_code != 200:
                sleep(1)
                if r.status_code == 404:
                    load_reviews(reviews)
                    return
                r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        items_count  = int(soup.find('span',  'tw-text-body-md').text.replace(',', '').replace('(', '').replace(')', '').strip())
        for review in soup.find_all(
            "div",
            class_="tw-pb-md md:tw-pb-lg tw-mb-md md:tw-mb-lg tw-pt-0 last:tw-pb-0",
        ):
            id = int(review.find("div").get("data-review-content-id"))
            rating = (
                review.find(
                    "div",
                    class_="tw-flex tw-relative tw-space-x-0.5 tw-w-[88px] tw-h-md",
                )
                .get("aria-label")
                .split("out")[0]
            )
            date = datetime.strptime(
                review.find("div", class_="tw-text-body-xs tw-text-fg-tertiary")
                .text.replace("Edited", "")
                .strip(),
                "%B %d, %Y",
            )
            reviewer_name = review.find(
                "div",
                class_="tw-text-heading-xs tw-text-fg-primary tw-overflow-hidden tw-text-ellipsis tw-whitespace-nowrap",
            ).get("title")
            reviewer_country, using_app = (
                review.find(
                    "div",
                    class_="tw-text-heading-xs tw-text-fg-primary tw-overflow-hidden tw-text-ellipsis tw-whitespace-nowrap",
                )
                .find_all_next("div")[0]
                .text.strip(),
                review.find(
                    "div",
                    class_="tw-text-heading-xs tw-text-fg-primary tw-overflow-hidden tw-text-ellipsis tw-whitespace-nowrap",
                )
                .find_all_next("div")[1]
                .text.strip(),
            )
            review_text = review.find("p", class_="tw-break-words").text.strip()
            if id not in scraped_ids:
                reviews.append(
                    {
                        "id": id,
                        "app_id": app_id,
                        "reviewer_name": reviewer_name,
                        "review_text": review_text,
                        "rating": rating,
                        "reviewer_time_using_app": using_app,
                        "time_of_update": datetime.now(),
                        "created_at": date,
                        "reviewer_country": reviewer_country,
                    }
                )
                scraped_ids.append(id)
        page += 1



BATCH_SIZE = 100_000


def load_reviews(reviews):
    with Session() as session:
        for i in range(0, len(reviews), BATCH_SIZE):
            batch = reviews[i : i + BATCH_SIZE]
            existing_review_ids = set(session.scalars(select(Review.id)).all())
            updates = [item for item in batch if item["id"] in existing_review_ids]
            inserts = [item for item in batch if item["id"] not in existing_review_ids]
            if updates:
                session.bulk_update_mappings(Review, updates)
            if inserts:
                session.bulk_insert_mappings(Review, inserts)
        session.commit()


def main():
    with Session() as session:
        app_ids = [app.id for app in session.query(App).all()]
    for app_id in app_ids:
        scrape_reviews(app_id)


if __name__ == "__main__":
    main()
