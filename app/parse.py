import csv
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int

PRODUCT_FIELDS = [product.name for product in fields(Product)]

def get_single_product(page_soup) -> Product:
    return Product(
        title=page_soup.select_one(".title")["title"],
        description=page_soup.select_one(".description.card-text").text.strip(),
        price=float(page_soup.find('span', itemprop='price').text.replace("$", "")),
        rating=int(page_soup.select_one('p[data-rating]')['data-rating']),
        num_of_reviews=int(page_soup.find('span', itemprop='reviewCount').text)
    )

def get_page_products(soup):
    products = soup.select(".product-wrapper.card-body")
    return [get_single_product(product) for product in products]

def get_all_products() -> None:
    text = requests.get(HOME_URL).content
    soup = BeautifulSoup(text, "html.parser")
    products = get_page_products(soup)

    with open('result.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(PRODUCT_FIELDS)
        prod_list = [astuple(product) for product in products]
        writer.writerows(prod_list)


if __name__ == "__main__":
    get_all_products()
