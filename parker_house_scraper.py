

columns = [
            "SKU", "START_DATE", "END_DATE", "DATE_QUALIFIER", "DISCONTINUED", "BRAND", "PRODUCT_GROUP1",
            "PRODUCT_GROUP2", "PRODUCT_GROUP3", "PRODUCT_GROUP4", "PRODUCT_GROUP1_QTY", "PRODUCT_GROUP2_QTY", 
            "PRODUCT_GROUP3_QTY", "PRODUCT_GROUP4_QTY", "DEPARTMENT1", "ROOM1", "ROOM2", "ROOM3", "ROOM4", 
            "ROOM5", "ROOM6", "CATEGORY1", "CATEGORY2", "CATEGORY3", "CATEGORY4", "CATEGORY5", "CATEGORY6", 
            "COLLECTION", "FINISH1", "FINISH2", "FINISH3", "MATERIAL", "MOTION_TYPE1", "MOTION_TYPE2", 
            "SECTIONAL", "TYPE1", "SUBTYPE1A", "SUBTYPE1B", "TYPE2", "SUBTYPE2A", "SUBTYPE2B", 
            "TYPE3", "SUBTYPE3A", "SUBTYPE3B", "STYLE", "SUITE", "COUNTRY_OF_ORIGIN", "MADE_IN_USA", 
            "BED_SIZE1", "FEATURES1", "TABLE_TYPE", "SEAT_TYPE", "WIDTH", "DEPTH", "HEIGHT", "LENGTH", 
            "INSIDE_WIDTH", "INSIDE_DEPTH", "INSIDE_HEIGHT", "WEIGHT", "VOLUME", "DIAMETER", "ARM_HEIGHT", 
            "SEAT_DEPTH", "SEAT_HEIGHT", "SEAT_WIDTH", "HEADBOARD_HEIGHT", "FOOTBOARD_HEIGHT", 
            "NUMBER_OF_DRAWERS", "NUMBER_OF_LEAVES", "NUMBER_OF_SHELVES", "CARTON_WIDTH", "CARTON_DEPTH", 
            "CARTON_HEIGHT", "CARTON_WEIGHT", "CARTON_VOLUME", "CARTON_LENGTH", "PHOTO1", "PHOTO2", 
            "PHOTO3", "PHOTO4", "PHOTO5", "PHOTO6", "PHOTO7", "PHOTO8", "PHOTO9", "PHOTO10", "INFO1", 
            "INFO2", "INFO3", "INFO4", "INFO5", "DESCRIPTION", "PRODUCT_DESCRIPTION", 
            "SPECIFICATIONS", "CONSTRUCTION", "COLLECTION_FEATURES", "WARRANTY", "ADDITIONAL_INFORMATION", 
            "DISCLAIMER", "VIEWTYPE", "ITEM_URL"
        ]






import scrapy
import os
from scrapy.crawler import CrawlerProcess
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv

class MenuScraper:    
    def scrape_navbar_to_csv():
        url = "https://parker-house.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the navigation div
        nav = soup.find("div", id="nav")
        direct_ul_children = nav.find("ul")
        direct_li_children = direct_ul_children.find_all("li", recursive=False)
        
        # Initialize the CSV file
        csv_file = "utilities/category-collection.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            # Initialize CSV writer with headers
            writer = csv.DictWriter(file, fieldnames=["category_name", "subcategory", "collection_name", "collection_link"])
            writer.writeheader()

            # Iterate through top-level categories
            for category_li in direct_li_children:
                category_name = category_li.find("a").text.strip()
                print(f"Category: {category_name}")

                # Check for subcategories
                subcategories_ul = category_li.find("ul")
                # print(subcategories_ul)
                # print("*"*30)
                # break
                if subcategories_ul:
                    categor = subcategories_ul.find_all("li", recursive=False)
                    for subcategory_li in categor:
                        subcategory_name = subcategory_li.find("a").text.strip()
                        
                        print(f"  Subcategory: {subcategory_name}")

                        # Check for collections under subcategories
                        collections_ul = subcategory_li.find("ul")
                        if collections_ul:
                            for collection_li in collections_ul.find_all("li", recursive=False):
                                collection_name = collection_li.find("a").text.strip()
                                collection_link = collection_li.find("a")["href"]
                                print(f"    Collection: {collection_name}")
                                if "collections" in subcategory_link and subcategory_name !=   "Collections":
                                    writer.writerow({
                                        "category_name": category_name,
                                        "subcategory": subcategory_name,
                                        "collection_name": collection_name.replace("-", ''),
                                        "collection_link": "https://parker-house.com" + collection_link
                                    })
                        else:
                            # No collections, treat subcategory as collection
                            subcategory_link = subcategory_li.find("a")["href"]

                            if "collections" in subcategory_link and subcategory_name !=   "Collections":
                                writer.writerow({
                                    "category_name": category_name,
                                    "subcategory": subcategory_name,
                                    "collection_name": subcategory_name.replace("-", ''),
                                    "collection_link": "https://parker-house.com" + subcategory_link
                                })
                else:
                    # No subcategories, treat category as both subcategory and collection
                    category_link = category_li.find("a").get("href")
                    if "collections" in subcategory_link and subcategory_name !=   "Collections":
                        writer.writerow({
                            "category_name": category_name,
                            "subcategory": category_name,
                            "collection_name": category_name.replace("-", ''),
                            "collection_link": "https://parker-house.com" + category_link
                        })

        print(f"Data has been saved to {csv_file}")
        
        
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------- 




def scrape_all_products(base_url):
    current_page = 1
    products = []

    while True:
        # Request the current page
        url = f"{base_url}?page={current_page}"
        print(f"Scraping: {url}")
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "html.parser")

        # Find all product links on the current page
        links = soup.find_all('a')
        for link in links:
            href = link.get("href")  # Get the href attribute
            if href and href.startswith("/collections/") and "/products/" in href:
                full_url = "https://parker-house.com" + href
                if full_url not in products:  # Avoid duplicates
                    products.append(full_url)
                    print(full_url)

        # Check for the "Next" page link
        next_page = soup.find("span", class_="next")
        if next_page and next_page.find("a"):
            current_page += 1  # Increment to the next page
        else:
            break  # No more pages, exit the loop

    return products

def process_collection_products(collection, all_products):
    category_name = collection['category_name']
    subcategory_name = collection["subcategory"]
    collection_name = collection['collection_name']
    collection_link = collection['collection_link']

    print(f"Processing category: {category_name}, collection: {collection_name}")

    # Scrape all products for the current collection
    product_links = scrape_all_products(collection_link)
    print(f"Products found: {len(product_links)}")

    # Add product data to the list
    for link in product_links:
        all_products.append({
            'category_name': category_name,
            'subcategory_name': subcategory_name,
            'collection_name': collection_name,
            'product_link': link
        })

def get_collections_products():
    # Ensure directories exist
    input_dir = 'utilities'
    os.makedirs(input_dir, exist_ok=True)


    input_file = os.path.join(input_dir, 'category-collection.csv')
    output_file = os.path.join(input_dir, 'products-links.csv')

    # Check if the input file exists; if not, create a sample file
    if not os.path.exists(input_file):
        print(f"{input_file} not found. Creating a sample file...")
        with open(input_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['category_name', 'subcategory', 'collection_name', 'collection_link'])
            writer.writeheader()
            writer.writerow({
                'category_name': 'Sample Category',
                'subcategory': 'Sample Subcategory',
                'collection_name': 'Sample Collection',
                'collection_link': 'https://example.com/collections/sample-collection'
            })
        print(f"Sample file created at {input_file}. Please update it with real data and rerun the script.")
        return

    all_products = []  # Initialize the list to hold all product data

    # Read the input CSV file
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        collections = [row for row in reader]

    # Process each collection
    for collection in collections:
        process_collection_products(collection, all_products)

    # Write the output to a CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['category_name', 'subcategory_name', 'collection_name', 'product_link'])
        writer.writeheader()
        writer.writerows(all_products)

    print("Scraping completed. Results saved to", output_file)





# ---------------------------------------------------------------------------------------------------------------------------------------------------------


     
class ProductSpider(scrapy.Spider):
    name = "product_spider"
    
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'HTTPERROR_ALLOW_ALL': True,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en',
        },
    }
    
    def start_requests(self):
        """Initial request handler."""
        self.logger.info("Spider started. Preparing to scrape products.")
        os.makedirs('output', exist_ok=True)
        self.scraped_data = []
        scraped_links = set()
        self.output_file = open('output/products-data.json', 'a', encoding='utf-8')
        if os.path.exists('output/products-data.json'):
            self.logger.info("Loading existing scraped data.")
            with open('output/products-data.json', 'r', encoding='utf-8') as f:
                    try:
                        self.scraped_data = json.load(f)
                        scraped_links = {(item['Product Link'], item["Collection"], item['Category']) for item in self.scraped_data}
                    except json.JSONDecodeError:
                        self.logger.warning("Encountered JSONDecodeError while loading existing data. Skipping line.")
                        pass 
        scraped_product_links = {item['Product Link'] for item in self.scraped_data}
        try:
            with open('utilities/products-links.json', 'r', encoding='utf-8') as file:
                products = json.load(file)
            self.logger.info(f"Loaded {len(products)} products to scrape.")
        except Exception as e:
            self.logger.error(f"Failed to load products-links.json: {e}")
            return
        for product in products:
            product_link = product['product_link']
            category_name = product['category_name']
            collection_name = product['collection_name']
            product_key = (product_link, collection_name, category_name)
            if product_key not in scraped_links:
                if product_link in scraped_product_links:
                    scraped_product = next((item for item in self.scraped_data if item['Product Link'] == product_link), None)
                    product_name = scraped_product["Product Title"]
                    if scraped_product:
                            if product_name:
                                if collection_name not in scraped_product['Collection'] or category_name not in scraped_product['Category']:
                                    new_product_data = scraped_product.copy()
                                    new_product_data['Collection'] = collection_name
                                    new_product_data['Category'] = category_name
                                    
                                    self.scraped_data.append(new_product_data)
                                    with open('output/products-data.json', 'w', encoding='utf-8') as f:
                                        json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)
                                    self.logger.info(f"Updated product with new collection or category: {product_link}")

                            else:
                                yield scrapy.Request(
                                    url=product_link,
                                    callback=self.parse,
                                    meta={
                                        'product': product
                                    }
                                )

                    else:
                        self.logger.warning(f"Product link found in scraped_product_links but not in scraped_data: {product_link}")
                else:
                    
                        yield scrapy.Request(
                            url=product_link,
                            callback=self.parse,
                            meta={
                                'product': product
                            }
                        )
            else:
                
                self.logger.info(f"Skipping already scraped product: {product_link} under category: {category_name}")


    def parse(self, response):
            """Parse the product page using BeautifulSoup and extract details."""
            self.logger.info(f"Parsing product: {response.url}")
            try:
                product = response.meta['product']
                soup = BeautifulSoup(response.text, 'html.parser')
                category_name = product['category_name']
                collection_name = product['collection_name']
                product_link = product['product_link']
                
                product_name = soup.find("div", class_="model_name font-FuturaPT-Book color-text-42210B")
                if product_name:
                    product_name = product_name.get_text().replace("\n", " ")
                else:
                    product_name = soup.find('div', class_="d-flex align-items-center collection-name mt-2")
                    if product_name:
                        product_name = product_name.get_text().replace("\n", " ")
                
                weight_dimensions_product_details = soup.find_all('div', class_="norm-desc ps-5 pe-5 mt-3 pb-4 description-box")
                product_details = []
                weights_dimensions = []
                if weight_dimensions_product_details:
                    for item in weight_dimensions_product_details:
                        label = item.find("p").text.strip()
                        if "Weights & Dimensions" in label:
                            weight_dimensions = item.find_all("li")
                            for li in weight_dimensions:
                                text = li.get_text(strip=True)
                                if ": " in text:
                                    key, value = text.split(": ", 1)
                                    dim = f"{key.strip()} : {value.strip()}"
                                    weights_dimensions.append(dim)
                        elif "Product Details" in label:
                            product_detail = item.find_all("li")
                            for detail in product_detail:
                                if detail.text.strip() != "Prop 65 Information":
                                    product_details.append(detail.text.strip())
                
                imgs = soup.find_all('a', class_="cloud-zoom-gallery")
                product_images = []
                for item in imgs:
                    product_images.append('https://www.homelegance.com' + item.get("href"))
                if product_images:
                    product_images = list(set(product_images))
                
                packaging = soup.find('div', class_="norm-desc ps-5 pe-5 mt-4 mb-4 pb-4")
                packaging_data = []
                if packaging:
                    packaging = packaging.find_all("li")
                    for li in packaging:
                        text = li.get_text(strip=True)
                        if ": " in text:
                            key, value = text.split(": ", 1)
                            if key != "Assembly Instruction":
                                pack = f"{key.strip()} : {value.strip()}"
                                packaging_data.append(pack)
                        if li.find("a"):
                            link = li.find("a").get("href")
                            packaging_data.append(f"Assembly Instruction : https://www.homelegance.com{link}")
                
                description = soup.find('div', class_="desc font-FuturaPT-Light collapse-description overflow-auto")
                if description:
                    description = description.text.strip()

                sku = ""
                if product_name:
                    sku = product_name.split()[0].strip()
                    product_name = product_name.replace(sku, "").strip()

                # Prepare the JSON structure
                new_product_data = {
                    'Category': category_name,
                    'Collection': collection_name,
                    'Product Link': product_link,
                    'Product Title': product_name,
                    "SKU": sku,
                    'Packaging': packaging_data,
                    'Product Details': product_details,  # Ensure this remains an array
                    'Weights & Dimensions': weights_dimensions,
                    "Product Images": product_images,
                    "Description": description
                }

                # Append to scraped data and write to file
                self.scraped_data.append(new_product_data)
                with open('output/products-data.json', 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, ensure_ascii=False, indent=4)
                
                self.logger.info(f"Successfully scraped product: {product_link}")

            except Exception as e:
                self.logger.error(f"Error parsing {response.url}: {e}")
    

    
    


   
#   -----------------------------------------------------------Run------------------------------------------------------------------------

def run_spiders():
    
    output_dir = 'utilities'
    os.makedirs(output_dir, exist_ok=True)
    products_links_scraper = MenuScraper()
    products_links_scraper.scrape_navbar_to_csv()

    get_collections_products()

    process = CrawlerProcess()
    process.crawl(ProductSpider)
    process.start()

run_spiders()