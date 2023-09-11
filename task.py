import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from csv import writer

prod_lst = []
driver = webdriver.Chrome()
driver.get('https://www.trendyol.com/yastik-x-c1206')
# print(driver.current_url)
time.sleep(10)
flag = False
while flag == False:
    products_end = driver.find_element(By.TAG_NAME, 'strong')
    driver.execute_script("arguments[0].scrollIntoView();", products_end)
    time.sleep(5)
    products = driver.find_elements(By.XPATH, '//div[@class="p-card-chldrn-cntnr card-border"]/a')
    time.sleep(5)
    with open('test.csv', 'a', newline="", encoding="utf8") as f:
        csv = writer(f)
        for product in products:
            link = product.get_attribute('href')
            if link not in prod_lst:
                print('Product added to CSV...')
                prod_lst.append(link)
                csv.writerow([link])
    print('Total Number of Products: ', len(prod_lst))
    for i in range(4):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
        time.sleep(1)
    if '95' in driver.current_url:
        print("Refreshing.....")
        driver.refresh()
    
    time.sleep(5)

    