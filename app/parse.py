import csv
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

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

def write_to_csv(products):
    with open('result.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(PRODUCT_FIELDS)
        prod_list = [astuple(product) for product in products]
        writer.writerows(prod_list)


def get_all_products():
    driver = webdriver.Chrome()
    driver.get(HOME_URL)
    nav_links = driver.find_elements(By.CSS_SELECTOR, ".sidebar-nav.navbar-collapse .nav-link")
    urls = [link.get_attribute("href") for link in nav_links]
    print(urls)
    results = []

    for url in urls:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "lxml")
        results.extend(get_page_products(soup))
    print(results)
    print(len(results))

    driver.quit()
    return results

    
if __name__ == "__main__":
    result = get_all_products()
    write_to_csv(result)
