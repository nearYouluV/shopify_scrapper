import requests
from bs4 import BeautifulSoup
from models import Session
from fake_useragent import UserAgent
from time import sleep
from models import *
from sqlalchemy import insert
import hashlib
from datetime import datetime
from sqlalchemy.orm import joinedload
from get_categories import headers, cookies
from reviews import scrape_reviews
from logger import logger
ua = UserAgent()
cat_url = "https://apps.shopify.com/categories/"


def get_full_category_tree():
    with Session() as session:
        return (
            session.query(Category)
            .options(joinedload(Category.subcategories).joinedload(Subcategory.tags))
            .all()
        )


def hash_app_data(app_data):
    return hashlib.sha256(str(app_data).encode()).hexdigest()


def scrape_items_from_categories(cat_link, cat_id, type: str):
    """Scraping categories page"""
    r = requests.get(cat_link, headers=headers, cookies=cookies)
    logger.info(f"Fetching {cat_link}")
    if r.status_code == 404:
        return
    if r.status_code != 200:
        sleep(10)
        while r.status_code != 200:
            r = requests.get(cat_link, headers=headers, cookies=cookies)
    soup = BeautifulSoup(r.text, "lxml")
    pagination = soup.find("div", attrs={"aria-label": "pagination"})
    try:
        page_count = int(pagination.find_all("a")[-2].text.strip()) if pagination else 1
    except:
        page_count = 1
    for page in range(1, page_count + 1):
        url = f"{cat_link}?page={page}"
        r = requests.get(url, headers=headers, cookies=cookies)
        if r.status_code != 200:
            sleep(10)
            r = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text, "lxml")
        for idx, app in enumerate(
            soup.find_all("div", attrs={"data-controller": "app-card"})
        ):
            is_ad = (
                True
                if app.find_previous("div").get(
                    "data-ads-waypoint-surface-intra-position"
                )
                else False
            )
            rank = ((page - 1) * 25) + (idx + 1)
            app_url = app.find("a").get("href")
            scrape_app_page(app_url, cat_id, rank, is_ad, type)


scraped_ids = []


def scrape_app_page(app_url, category_id=None, rank=None, is_ad=None, type: str = None):
    """Scraping app page"""
    app_id = app_url.split("/")[-1].split("?")[0]
    try:
        with Session() as session:
            if type == "cat":
                session.execute(
                    insert(app_category_association).values(
                        app_id=app_id,
                        category_id=category_id,
                        app_rank=rank,
                        is_ad=is_ad,
                    )
                )
            elif type == "sub":
                session.execute(
                    insert(app_subcategory_association).values(
                        app_id=app_id,
                        subcategory_id=category_id,
                        app_rank=rank,
                        is_ad=is_ad,
                    )
                )
            elif type == "tag":
                session.execute(
                    insert(app_tag_association).values(
                        app_id=app_id, tag_id=category_id, app_rank=rank, is_ad=is_ad
                    )
                )
            session.commit()
    except:
        pass
    if app_id in scraped_ids:

        return
    r = requests.get(app_url, headers={"User-Agent": ua.random})
    if r.status_code == 404:
        return
    if r.status_code != 200:
        sleep(10)
        while r.status_code != 200:
            try:
                r = requests.get(app_url, headers={"User-Agent": ua.random})
            except:
                sleep(2)
                r = requests.get(app_url, headers={"User-Agent": ua.random})
    logger.info(f"Scraping {app_url}")
    soup = BeautifulSoup(r.text, "lxml")
    app_name = soup.find("h1").text.strip()

    scraped_ids.append(app_id)
    for i in soup.find_all("dt"):
        if "Developer" in i.text:
            developer_link = i.find_next("a").get("href")
            developer_name = i.find_next("a").text.strip()
            break
    developer_website = None
    
    for i in soup.find_all('div', class_='tw-grid tw-grid-cols-4 tw-gap-x-gutter--mobile lg:tw-gap-x-gutter--desktop tw-border-t tw-border-t-stroke-secondary tw-pt-sm'):
        for k in i.find_all("a"):
            if "Website" in k.text:
                developer_website = k.get("href")
                break

    works_with, launched_date, languages, dev_address = None, None, None, None
    for i in soup.find_all(
        "h3",
        class_="tw-col-span-full sm:tw-col-span-1 tw-text-heading-sm sm:tw-text-heading-xs tw-mb-xs sm:tw-mb-0",
    ):
        if "Developer" in i.text:
            dev_address = (
                i.find_next(
                    "p", class_="tw-text-fg-tertiary tw-text-body-md"
                ).text.strip()
                if i.find_next("p", class_="tw-text-fg-tertiary tw-text-body-md")
                else None
            )
    for i in soup.find_all(
        "p",
        class_="tw-col-span-full sm:tw-col-span-1 tw-text-heading-sm sm:tw-text-heading-xs tw-mb-xs sm:tw-mb-0",
    ):
        if "Launched" in i.text:
            try:
                launched_date = datetime.strptime(
                    i.find_next("p")
                    .text.replace("·", "")
                    .replace("Changelog", "")
                    .strip(),
                    "%B %d, %Y",
                )
            except:
                logger.error(f"Error parsing launched date for {app_url}")
        elif "Works with" in i.text:
            works_with = ", ".join(
                [k.text.strip() for k in i.find_next("ul").find_all("li")]
            )
        elif "Languages" in i.text:
            languages = i.find_next("p").text.replace("and", ",").strip()
    built_for_shopify = (
        True
        if soup.find(
            "span",
            class_="tw-inline-flex tw-self-start tw-items-center tw-rounded-xs tw-whitespace-nowrap tw-py-3xs tw-px-sm tw-text-label-sm tw-leading-xl tw-bg-canvas-accent-bfs tw-text-fg-primary built-for-shopify-badge",
        )
        else False
    )
    pricing_data = []
    for price_info in soup.find_all("div", class_="app-details-pricing-plan-card"):
        price_text = price_info.find(
            "h3",
            attrs={
                "class": "app-details-pricing-format-group tw-flex tw-items-end tw-gap-xs tw-overflow-hidden tw-text-ellipsis"
            },
        ).text.strip()
        price = (
            float(
                price_text.replace("$", "")
                .replace(",", "")
                .split("/")[0]
                .split("\n")[0]
            )
            if "free" not in price_text.lower()
            else 0
        )
        currency = "$"
        try:
            model = price_info.find("p", attrs={"data-test-id": "name"}).text.strip()
        except:
            model = ""
        try:
            details = price_info.find(
                "ul", attrs={"data-test-id": "features"}
            ).text.strip()
        except:
            details = ""
        pricing_data.append(
            {
                "app_id": app_id,
                "price": price,
                "plan_name": model,
                "details": details,
                "currency": currency,
            }
        )
    app_hash = hash_app_data(
        {
            "name": app_name,
            "developer_name": developer_name,
            "pricing": pricing_data,
            "languages": languages,
            "works_with": works_with,
        }
    )
    for i in soup.find_all("div", class_="tw-grid tw-grid-cols-4 tw-gap-x-gutter--mobile lg:tw-gap-x-gutter--desktop tw-border-t tw-border-t-stroke-secondary tw-pt-sm"):
        if 'Categories' in i.text:
            categories = i.find_next('div').find_all('a')
            categories = ', '.join([cat.text.strip() for cat in categories])
            categories_link = ', '.join([cat.get('href') for cat in i.find_next('div').find_all('a')])
    app_data = {
        "id": app_id,
        "name": app_name,
        "url": app_url,
        "languages": languages,
        "works_with": works_with,
        "built_for_shopify": built_for_shopify,
        "developer_name": developer_name,
        "launched_at": launched_date,
        "categories": categories,
        "categories_link": categories_link
    }
    with Session() as session:
        existing_app = session.query(App).filter_by(id=app_id).first()
        if existing_app and existing_app.hash == app_hash:
            return
        if not existing_app:
            save_or_update_app(app_data=app_data, new_hash=app_hash)
        elif existing_app and existing_app.hash != app_hash:
            dev_id = session.query(Developer).filter_by(name=developer_name).first().id
            old_app = AppVersion(
                app_id=existing_app.id,
                name=existing_app.name,
                url=existing_app.url,
                developer_name=existing_app.developer_name,
                languages=existing_app.languages,
                works_with=existing_app.works_with,
                built_for_shopify=existing_app.built_for_shopify,
                recorded_at=datetime.utcnow(),
                developer_id=dev_id,
                hash=existing_app.hash,
            )
            session.add(old_app)
            session.commit()

            save_or_update_app(app_data, new_hash=app_hash)
            save_pricing(
                app_id=app_id, app_version_id=old_app.id, pricing_data=pricing_data
            )
        if developer_name != "unknown":
            if not session.query(Developer).filter_by(name=developer_name).first():
                session.add(
                    Developer(
                        link=developer_link, name=developer_name, address=dev_address, website=developer_website
                    )
                )
        save_pricing(app_id=app_id, pricing_data=pricing_data)

        session.commit()


def main():
    categories = get_full_category_tree()
    for category in categories:
        link = f"{cat_url}{category.id}".replace("---", "-").replace("--", "-")
        logger.info(f"Processing category link: {link}")
        type = "cat"
        scrape_items_from_categories(cat_link=link, cat_id=category.id, type=type)
        for subcategory in category.subcategories:
            type = "sub"
            link = f"{cat_url}{category.id}-{subcategory.id}".replace(
                "---", "-"
            ).replace("--", "-")
            logger.info(f"Processing subcategory link: {link}")
            scrape_items_from_categories(
                cat_link=link, cat_id=subcategory.id, type=type
            )
            for tag in subcategory.tags:
                logger.info(f"Processing tag link: {link}")
                type = "tag"
                link = f"{cat_url}{category.id}-{subcategory.id}-{tag.id}".replace(
                    "---", "-"
                ).replace("--", "-")
                scrape_items_from_categories(cat_link=link, cat_id=tag.id, type=type)

    # --- You can coment this part and run reviews directly from reviews.py, otherwise this code will take much more time ---            
    with Session() as session:
        app_ids = [app.id for app in session.query(App).all()]
    for app_id in app_ids:
        scrape_reviews(app_id)
    #--- ---


if __name__ == "__main__":
    main()
