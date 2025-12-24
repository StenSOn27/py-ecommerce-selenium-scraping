import csv
import time
from dataclasses import astuple, dataclass, fields
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://webscraper.io/test-sites/e-commerce/more/"

PAGES_TO_SCRAPE = {
    "home": "",
    "computers": "computers",
    "laptops": "computers/laptops",
    "tablets": "computers/tablets",
    "phones": "phones",
    "touch": "phones/touch"
}

@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int

PRODUCT_FIELDS = [field.name for field in fields(Product)]

def get_page_products(soup):
    products = []
    items = soup.select(".product-wrapper.card-body")
    
    for item in items:
        try:
            title_tag = item.select_one(".title")
            price_tag = item.select_one(".price")
            desc_tag = item.select_one(".description")
            rating_tag = item.select_one("p[data-rating]")
            reviews_tag = item.select_one(".review-count")

            if title_tag and price_tag:
                products.append(Product(
                    title=title_tag["title"],
                    description=desc_tag.text.strip() if desc_tag else "",
                    price=float(price_tag.text.replace("$", "")),
                    rating=int(rating_tag["data-rating"]) if rating_tag else 0,
                    num_of_reviews=int(reviews_tag.text.split()[0]) if reviews_tag else 0
                ))
        except Exception:
            continue
            
    return products

def write_to_csv(products, filename):
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(PRODUCT_FIELDS)
        for product in products:
            writer.writerow(astuple(product))

def load_all_items(driver):
    wait = WebDriverWait(driver, 3)
    while True:
        try:
            driver.execute_script("var x = document.getElementById('cookieBanner'); if(x) x.remove();")
            
            more_btn = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ecomerce-items-scroll-more, .btn-primary"))
            )
            
            if more_btn.is_displayed():
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(0.5) 
            else:
                break
        except Exception:
            break

def get_all_products():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    try:
        for filename, url_suffix in PAGES_TO_SCRAPE.items():
            full_url = urljoin(BASE_URL, url_suffix)
            products = []
            
            try:
                driver.get(full_url)
                load_all_items(driver)
                
                soup = BeautifulSoup(driver.page_source, "lxml")
                products = get_page_products(soup)
            except Exception:
                pass
            finally:
                write_to_csv(products, filename)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    get_all_products()