import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from csv import writer
import requests
import xml.etree.ElementTree as ET

class Initializer:
    def __init__(self):
        self.product_links = []
        
class Browser:
    def session(self):
        options = Options()
        options.add_argument("--lang=en")
        prefs = {
        "translate_whitelists": {"tr":"en"},
        "translate":{"enabled":"true"}
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_script_timeout(10)

class CSV:
    def __init__(self, filename):
        self.filename = filename

    def make_csv(self, filename):
        with open(filename, mode="w", encoding="utf8", newline="") as f:
            csv = writer(f)
            columns = ['Product Link','Title','Price','Original Price','Discounted Price','Sizes','Rating','Product Description','Images','Reviews','Color','Product Attributes']
            csv.writerow(columns)

    def populate_csv(self, data, filename):
        with open(filename, mode="a", encoding="utf8", newline="") as f:
            csv = writer(f)
            csv.writerow(data)


class Scraper(Initializer, Browser, CSV):
    def read_xml(self, xml_url):
        sitemap_url = xml_url
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            self.category_links = [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        else:
            print("Failed to fetch the sitemap. Status code:", response.status_code)

    def collect_products(self,filename):
        for category_link in self.category_links:
            print(category_link)
            self.driver.get('https://www.trendyol.com/en/running-training-shoes-x-c101426')
            time.sleep(15)
            
            try:
                accept_btn = self.driver.find_element(By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
                accept_btn.click()
            except:
                pass

            try:
                country_input = self.driver.find_element(By.XPATH, '//div[@class="country-select"]/select')
                country_input.click()
                country_input.send_keys('Turkey')
                country_input.send_keys(Keys.ENTER)
                time.sleep(1)
                country_select = self.driver.find_element(By.XPATH, '//div[@class="country-actions"]/button')
                country_select.click()

            except:
                pass

            try:
                accept_btn = self.driver.find_element(By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
                accept_btn.click()
            except:
                pass
            time.sleep(2)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

            self.driver.find_element(By.XPATH, '//div[@class="srch-rslt-cntnt"]').click()
            time.sleep(2)
            flag = True
            while flag:
                # time.sleep(2)
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                if self.driver.execute_script("return window.pageYOffset + window.innerHeight") >= last_height:
                    time.sleep(5)
                    products = self.driver.find_elements(By.XPATH, '//div[@class="p-card-chldrn-cntnr card-border"]/a')
                    for product in products:
                        self.product_links.append(product.get_attribute('href'))
                    break
                else:
                    for i in range(3):
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                        time.sleep(2)
                    # for i in range(1):
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                    time.sleep(1)
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    products = self.driver.find_elements(By.XPATH, '//div[@class="p-card-chldrn-cntnr card-border"]/a')
                    print(len(products))
            time.sleep(15)
            print(len(self.product_links))
            self.collect_product_info(filename)

        print(self.product_links)

    def collect_product_info(self, filename):
        for product_link in self.product_links:
            self.driver.get(product_link)
            time.sleep(20)
            self.driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(2)

            #title
            title_lst = []
            try:
                title = self.driver.find_element(By.TAG_NAME, 'h1')
                title_lst.append(title.text)
                print(title_lst)
            except:
                title_lst.append("Not Found")

            time.sleep(1)
            #images
            image_lst = []
            try:
                preview_images = self.driver.find_elements(By.XPATH, '//div[@class="gallery-container"]//div[@class="styles-module_slider__o0fqa"]/div')
                no_of_images = len(preview_images)
                base_image = self.driver.find_element(By.XPATH,'//div[@class="base-product-image"]')
                base_image.click()
                time.sleep(1)
                for i in range(no_of_images):
                    next_button = self.driver.find_element(By.XPATH, '//i[@class="gallery-modal-icon i-arrow-right right"]')
                    images = self.driver.find_element(By.XPATH, '//div[@class="gallery-modal-content"]//img')
                    if images.get_attribute('src') in image_lst:
                        break
                    else:
                        image_lst.append(images.get_attribute('src'))
                    next_button.click()
                close_image = self.driver.find_element(By.XPATH, '//i[@class="i-close"]')
                close_image.click()
                print(image_lst)

            except:
                image_lst.append("Not Found")

            time.sleep(1)

            #price
            price_lst = []
            original_price_lst = []
            discounted_price_lst = []
            try:
                price_section = self.driver.find_element(By.XPATH, '//div[@class="featured-prices"]')
                price_lst.append("Not Found")
                try:
                    original_price = self.driver.find_element(By.XPATH, '//div[@class="featured-prices"]/span[@class="prc-org"]')
                    original_price_lst.append(original_price.text)
                except:
                    original_price_lst.append("Not Found")
                try:
                    discounted_price = self.driver.find_element(By.XPATH, '//div[@class="featured-prices"]/span[@class="prc-dsc"]')
                    discounted_price_lst.append(discounted_price.text)
                except:
                    discounted_price_lst.append("Not Found")
                
            except:
                try:
                    price = self.driver.find_element(By.XPATH, '//div[@class="product-price-container"]//span[@class="prc-dsc"]')
                    price_lst.append(price.text)
                    original_price_lst.append("Not Found")
                    discounted_price_lst.append("Not Found")
                except:
                    price_lst.append("Not Found")
                    original_price_lst.append("Not Found")
                    discounted_price_lst.append("Not Found")

            print(price_lst)
            print(original_price_lst)
            print(discounted_price_lst)

            time.sleep(1)

            #color
            color_lst = []
            try:
                colors = self.driver.find_elements(By.XPATH, '//div[@class="attributeSlider"]//div[@class="styles-module_slider__o0fqa"]//a')
                for color in colors:
                    color_lst.append(color.text)
            except:
                color_lst.append("Not Found")

            print(color_lst)

            time.sleep(1)
            
            #size
            size_lst = []
            try:
                sizes = self.driver.find_elements(By.XPATH, '//div[@class="variants"]//div[@class="styles-module_slider__o0fqa"]/div')
                for size in sizes:
                    size_lst.append(size.text)
                print(size_lst)
            except:
                size_lst.append("Not Found")

            time.sleep(1)

            #product 
            product_desc_lst = []
            try:
                decriptions = self.driver.find_elements(By.XPATH, '//div[@class="info-wrapper"]')
                for description in decriptions:
                    product_desc_lst.append(description.text)
                print(product_desc_lst)
            except:
                product_desc_lst.append("Not Found")

            time.sleep(1)

            attribute_lst = []
            attrs = []
            attrs_values = []
            try:
                detail_attrs = self.driver.find_elements(By.XPATH, '//li[@class="detail-attr-item"]/span[1]')
                for detail_attr in detail_attrs:
                    attrs.append(detail_attr.text)
                detail_attrs_values = self.driver.find_elements(By.XPATH, '//li[@class="detail-attr-item"]/span[2]')
                for value in detail_attrs_values:
                    attrs_values.append(value.text)
            except:
                attribute_lst.append("Not Found")
                print(attribute_lst)
            print(attrs)
            print(attrs_values)

            detail_attrs_lst = list(zip(attrs, attrs_values))
            print(detail_attrs_lst)

            time.sleep(1)

            rating_lst = []
            try:
                rating = self.driver.find_element(By.XPATH, '//div[@class="pr-rnr-sm-p"]')
                rating_lst.append(rating.text)
                print(rating_lst)
            except:
                rating_lst.append("Not Found")

            time.sleep(1)

            review_lst = []
            try:
                review_button = self.driver.find_element(By.XPATH, '//a[@class="pr-rnr-mr-btn gnr-cnt-br"]')
                self.driver.get(review_button.get_attribute('href'))
                time.sleep(15)
                flag = False
                while flag == False:
                    print('here')
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    if self.driver.execute_script("return window.pageYOffset + window.innerHeight") >= last_height:
                        time.sleep(5)
                        reviews = self.driver.find_elements(By.XPATH, '//div[@class="comment-text"]/p')
                        for review in reviews:
                            review_lst.append(review.text)
                        break
                    else:
                        for i in range(2):
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(3)
                print(review_lst)
            except:
                review_lst.append("Not Found")

            time.sleep(1)
            
            for i,j,k,l,m,n,o in zip(title_lst, price_lst, original_price_lst, discounted_price_lst, rating_lst, product_desc_lst):
                data = [self.driver.current_url(),i,j,k,l,m,n,o,[size_lst],[image_lst],[review_lst],[color_lst],[detail_attrs_lst]]
            super().populate_csv(data, filename)


class Scraper_Implementor(Scraper):
    def scrape(self, xml_url, filename):
        super().make_csv(filename)
        super().read_xml(xml_url)
        super().session()
        time.sleep(5)
        super().collect_products(filename)
        # super().collect_product_info(filename)

obj = Scraper_Implementor()
obj.scrape("https://www.trendyol.com/en/sitemap_categories.xml", "output.csv")



