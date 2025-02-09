
import scrapy
import os
from scrapy.crawler import CrawlerProcess
import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_navbar_to_csv():
    url = "https://parker-house.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    nav = soup.find("div", id="nav")
    direct_ul_children = nav.find("ul")
    direct_li_children = direct_ul_children.find_all("li", recursive=False)
    csv_file = "utilities/category-collection.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["category_name", "subcategory", "collection_name", "collection_link"])
        writer.writeheader()
        for category_li in direct_li_children:
            category_name = category_li.find("a").text.strip()
            print(f"Category: {category_name}")
            subcategories_ul = category_li.find("ul")
            if subcategories_ul:
                categor = subcategories_ul.find_all("li", recursive=False)
                for subcategory_li in categor:
                    subcategory_name = subcategory_li.find("a").text.strip()
                    
                    print(f"  Subcategory: {subcategory_name}")
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
                                if ("/pages/" in subcategory_link and subcategory_name != "Collections" and category_name not in {"Sign in", "Collections"}): 
                                    writer.writerow({
                                    "category_name": category_name,
                                    "subcategory": subcategory_name,
                                    "collection_name": collection_name.replace("-", ''),
                                    "collection_link": "https://parker-house.com" + collection_link
                                    })
                    else:
                        subcategory_link = subcategory_li.find("a")["href"]

                        if "collections" in subcategory_link and subcategory_name !=   "Collections":
                            writer.writerow({
                                "category_name": category_name,
                                "subcategory": subcategory_name,
                                "collection_name": subcategory_name.replace("-", ''),
                                "collection_link": "https://parker-house.com" + subcategory_link
                            })
                        else:
                            if ("/pages/" in subcategory_link and subcategory_name != "Collections" and category_name not in {"Sign in", "Collections"}):  
                                writer.writerow({
                                    "category_name": category_name,
                                    "subcategory": subcategory_name,
                                    "collection_name": subcategory_name.replace("-", ''),
                                    "collection_link": "https://parker-house.com" + subcategory_link
                                })                               
            else:
                category_link = category_li.find("a").get("href")
                if "collections" in subcategory_link and subcategory_name !=   "Collections":
                    writer.writerow({
                        "category_name": category_name,
                        "subcategory": category_name,
                        "collection_name": category_name.replace("-", ''),
                        "collection_link": "https://parker-house.com" + category_link
                    })
                else:
                    if ("/pages/" in subcategory_link and subcategory_name != "Collections" and category_name not in {"Sign in", "Collections"}):
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
        url = f"{base_url}?page={current_page}"
        print(f"Scraping: {url}")
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "html.parser")
        links = soup.find_all('a')
        for link in links:
            href = link.get("href") 
            if href and href.startswith("/collections/") and "/products/" in href:
                full_url = "https://parker-house.com" + href
                if full_url not in products: 
                    products.append(full_url)
                    # print(full_url)

            
            elif href and href.startswith("https://parker-house.com/products/"):
                full_url = href
                if full_url not in products: 
                    products.append(full_url)
                    # print(full_url)

                
        next_page = soup.find("span", class_="next")
        if next_page and next_page.find("a"):
            current_page += 1  
        else:
            break  
    return products

def process_collection_products(collection, all_products):
    category_name = collection['category_name']
    subcategory_name = collection["subcategory"]
    collection_name = collection['collection_name']
    collection_link = collection['collection_link']

    print(f"Processing category: {category_name}, collection: {collection_name}")

    product_links = scrape_all_products(collection_link)

    if len(product_links) ==0:
        product_links = []
        print(f"Products found: {len(product_links)}")
        print("So , there are some some collections")
        print("Processing subcollection")
        req = requests.get(collection_link)
        soup = BeautifulSoup(req.content, "html.parser")
        links = soup.find_all('a')
        for link in links:
            href = link.get("href") 
            if ((href and href.startswith("https://parker-house.com/collections/")) and link.find("img")and subcategory_name!= "Motion"):
                product_links = scrape_all_products(href)
                print(f"Products found: {len(product_links)}")
                for item in product_links:
                    all_products.append({
                        'category_name': category_name,
                        'subcategory_name': subcategory_name,
                        'collection_name': collection_name,
                        'product_link': item
                    })
    else:   
        print(f"Products found: {len(product_links)}")
        for link in product_links:
            all_products.append({
                'category_name': category_name,
                'subcategory_name': subcategory_name,
                'collection_name': collection_name,
                'product_link': link
            })

def get_collections_products():
    input_dir = 'utilities'
    os.makedirs(input_dir, exist_ok=True)


    input_file = os.path.join(input_dir, 'category-collection.csv')
    output_file = os.path.join(input_dir, 'products-links.csv')

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

    all_products = [] 

    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        collections = [row for row in reader]

    for collection in collections:
        process_collection_products(collection, all_products)

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

    def __init__(self, input_file='utilities/products-links.csv', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_file = input_file
        os.makedirs('output', exist_ok=True)
        self.parker_house_file = open('output/parker_house.csv', 'w', newline='', encoding='utf-8')
        self.parker_living_file = open('output/parker_living.csv', 'w', newline='', encoding='utf-8')

        self.parker_house_writer = csv.DictWriter(self.parker_house_file, fieldnames=self.columns)
        self.parker_living_writer = csv.DictWriter(self.parker_living_file, fieldnames=self.columns)

        self.parker_house_writer.writeheader()
        self.parker_living_writer.writeheader()

    def start_requests(self):
        self.logger.info("Spider started. Reading product links from CSV file.")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield scrapy.Request(
                    url=row['product_link'],
                    callback=self.parse,
                    meta={
                        'category_name': row['category_name'],
                        'subcategory_name': row['subcategory_name'],
                        'collection_name': row['collection_name'],
                        'product_link': row['product_link']
                    }
                )
    def parse(self, response):
        self.logger.info(f"Parsing product: {response.url}")
        features = []
        sku = ""
        product_title = ""
        width = ""
        depth = ""
        height = ""
        description = ""
        material = ""
        finish = ""
        products_images = []
        try:
            meta = response.meta
            soup = BeautifulSoup(response.text, 'html.parser')

            data = {col: "" for col in self.columns} 


            try:
                sku_element = soup.select_one('p.sku span[itemprop="sku"]')
                if sku_element:
                    sku = sku_element.text.strip()
                if not sku:
                    sku_p_tag = None
                    for p_tag in soup.find_all("p"):
                        if "SKU:" in p_tag.get_text():
                            sku_p_tag = p_tag
                            break
                    if sku_p_tag:
                        cleaned_text = re.sub(r"<[^>]*>", " ", str(sku_p_tag))
                        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
                        match = re.search(r"SKU:\s*(\S+)", cleaned_text, flags=re.IGNORECASE)
                        if match:
                            sku = match.group(1).strip()
                if not sku or sku == "**":
                    try:
                        sku = meta['product_link'].split("/")[-1].upper()
                    except AttributeError:
                        sku = ""
                if sku:
                    print("The Product SKU is:", sku)
                else:
                    print("SKU not found.")
            except Exception as e:
                print("An error occurred while extracting SKU:", str(e))

            
            if sku:
                sku = sku.replace("*", "").replace("#", "")


            try:
                product_title = soup.find("h1", class_="product_name")
                if product_title:
                    product_title = product_title.text.strip()
            except AttributeError:
                product_title = ""

            try:
                width = soup.find("td", text="Width").find_next_sibling("td").text.strip().replace(" in", "")
            except AttributeError:
                width = ""

            try:
                depth = soup.find("td", text="Depth").find_next_sibling("td").text.strip().replace(" in", "")
            except AttributeError:
                depth = ""

            try:
                height = soup.find("td", text="Height").find_next_sibling("td").text.strip().replace(" in", "")
            except AttributeError:
                height = ""

            try:
                description_id = soup.find("a", text="Description")
                if description_id:
                    description_id = description_id.get("href").replace("#", "")
                    description = soup.find("div", id=description_id).find("p").text.strip()
                else:
                    description = ""
            except AttributeError:
                description = ""

            try:
                color_id = soup.find("a", text="Color")
                if color_id:
                    color_id = color_id.get("href").replace("#", "")
                    color = soup.find("div", id=color_id)
                else:
                    color = None
            except AttributeError:
                color = None


            if color:
                p_tag = color.find("p")
                if p_tag:
                    raw_text = str(p_tag)
                    clean_text = re.sub(r"<[^>]*>", " ", raw_text)
                    clean_text = re.sub(r"SKU:\s*\S+", " ", clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r"\s+", " ", clean_text).strip()
                    if "Finish:" in clean_text:
                        finish_start = clean_text.find("Finish:") + len("Finish:")
                        finish_end = clean_text.find("Material:") if "Material:" in clean_text else len(clean_text)
                        finish = clean_text[finish_start:finish_end].strip()
                    if "Material:" in clean_text:
                        material_start = clean_text.find("Material:") + len("Material:")
                        material_end = clean_text.find("Also Available In:") if "Also Available In:" in clean_text else len(clean_text)
                        material = clean_text[material_start:material_end].strip()

            try:
                features_id = soup.find("a", text="Features")
                if features_id:
                    features_id = features_id.get("href").replace("#", "")
                    features = [li.text.strip() for li in soup.find("div", id=features_id).find_all("li")]
            except AttributeError:
                features = ""
            sub_category = ""
            if meta['subcategory_name']:
                if "Leather Reclining" in meta['subcategory_name']:
                    sub_category = "Leather Reclining"
                else:
                    sub_category = meta['subcategory_name']

            if product_title:
                dash_count = product_title.count("-")
                if dash_count == 1:
                    collection_name = product_title.split("-")[0].strip()

                else:
                    collection_name = meta['collection_name']
                    

            data.update({
                "CATEGORY1": meta['category_name'],
                "CATEGORY2": sub_category,
                "COLLECTION": collection_name,
                "ITEM_URL": meta['product_link'],
                "SKU": sku,
                "DESCRIPTION": product_title,
                "PRODUCT_DESCRIPTION": description,
                "WIDTH": width,
                "DEPTH": depth,
                "HEIGHT": height,
                "ADDITIONAL_INFORMATION": material,
                "FINISH1": finish,
                "CONSTRUCTION": ", ".join(features) if isinstance(features, list) else features,
                # "BRAND": "Parker House", 
                "BRAND": "Parker Living" if meta['category_name'] == "Upholstery" else "Parker House",
                "VIEWTYPE": "Normal",   
            })

            try:
                products_img = soup.find_all("a", class_="fancybox")
                if products_img:
                    products_images = list(set(["https:" + item.get("href") for item in products_img]))
                else:
                    products_images = []
            except AttributeError:
                products_images = []
            for i in range(1, 11):
                data[f"PHOTO{i}"] = ""
            for idx, img_url in enumerate(products_images):
                if idx > 9:
                    continue
                else:
                    data[f"PHOTO{idx + 1}"] = img_url
            if len(products_images) < 10:
                self.logger.info(f"Only {len(products_images)} images found for {meta['product_link']}. Remaining PHOTO columns will be ''.")
            elif len(products_images) > 10:
                self.logger.warning(f"More than 10 images found for {meta['product_link']}. Only the first 10 will be saved.")

            elif len(products_images) == 0:
                data.update({
                    "VIEWTYPE": "Normal",
                })

            if meta['category_name'] == "Upholstery":
                self.parker_living_writer.writerow(data)
            else:
                self.parker_house_writer.writerow(data)

            self.logger.info(f"Successfully scraped and categorized product: {meta['product_link']}")
        except Exception as e:
            self.logger.error(f"Error parsing product: {response.url}, {e}")

    def closed(self, reason):
        self.parker_house_file.close()
        self.parker_living_file.close()
        self.logger.info("Spider closed. Files saved.")
   
#   -----------------------------------------------------------Run------------------------------------------------------------------------

def run_spiders():
    output_dir = 'utilities'
    os.makedirs(output_dir, exist_ok=True)
    scrape_navbar_to_csv()
    get_collections_products()
    process = CrawlerProcess()
    process.crawl(ProductSpider)
    process.start()


run_spiders()