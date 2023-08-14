from bs4 import BeautifulSoup, Tag
import requests
import time


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

def document_initialised(driver):
    return driver.execute_script("return initialised")

def trial(search):
    service = Service('C:/chrome/chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    url = "%s%s" %("https://tmpnponline.co.zw/?post_type=product&s=",search) #bad
    url3 = "%s%s" %("https://www.spar.co.zw/products?q=",search)
    url2 = "https://tmpnponline.co.zw/"
    url4 = "%s%s%s" %("https://okonline.co.zw/?s=",search,"&post_type=product&dgwt_wcas=1")
    url5 = "%s%s%s" %("https://freshinabox.org/search?q=",search,"&options%5Bprefix%5D=last")
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = True

    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)

    # getting GeekForGeeks webpage
    driver.get(url5)
    time.sleep(20)
    # WebDriverWait(driver, timeout=10).until(document_initialised)
    # elem = driver.find_element(By.CSS_SELECTOR, 'ul.products')
    # elem = driver.find_element(By.NAME, "phrase")
    # elem.send_keys("peache")
    # elem.send_keys(Keys.RETURN)
    
    file = open(driver.page_source,"a", encoding='utf8')
    file.write(driver.page_source)
    print(file)
    # print(driver.page_source)
    # soup = BeautifulSoup(file, 'html.parser')

    # print(elem)

    # We can also get some information 
    # about page in browser.
    # So let's output webpage title into
    # terminal to be sure that the browser
    # is actually running.
    # print(driver.page_source)

    # close browser after our manipulations
    driver.close()

def getSpar(search):
    service = Service('C:/chrome/chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
 
    url3 = "%s%s" %("https://www.spar.co.zw/products?q=",search)
 
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = True

    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)

    # getting GeekForGeeks webpage
    driver.get(url3)
    time.sleep(5)

    # add html to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")


    products = soup.find_all("li")
    products_list = []
    for product in products:
        name = product.find("p")
        # check if name exists
        if name is not None:
            name = name.text

        price = product.find("strong")
        if price is not None:
            price = price.text

        image = product.find("a")

        #  if name is missing  dont add products
        if name != None:
            product = []
            # if image:
            #     image_url = image.get("style").split("(")[1].split(")")[0]  
            # else:
            #     image_url = None
            product.append(name)
            product.append(price.split('$')[1])
            product.append(image)
            product.append("Spar Supermarket")
            products_list.append(product)


    # close browser after our manipulations
    # print(products_list)
    driver.close()
    return products_list

def getFreshInABox(search):
    service = Service('C:/chrome/chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
 
    url = "%s%s%s" %("https://freshinabox.org/search?q=",search,"&options%5Bprefix%5D=last")
 
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = True

    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)

    # getting GeekForGeeks webpage
    driver.get(url)
    time.sleep(8)

    # add html to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    products = soup.find_all("div", {"class": "product__card__content"})
    # product__card mb-30 
    products_list = []
    for product in products:
        name = product.find("h3")
        if name is not None:
            name = name.text
        price = product.find("span", {"class":"price-item"})
        if price is not None:
            price = price.text
        image = product.find("a")


        #  if name is missing  dont add products
        if name != None:
            product = []
            # if image:
            #     image_url = image.get("style").split("(")[1].split(")")[0]  
            # else:
            #     image_url = None
            new_price = price.replace('\n','')
            new_price.strip()
            product.append(name)
            product.append(new_price)
            product.append(image)
            product.append("Fresh in a Box")

          

            products_list.append(product)

    # close browser after our manipulations
    driver.close()
    return products_list


def getOkaySuperMarket(search):
    service = Service('C:/chrome/chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
 
    
    url = "%s%s%s" %("https://okonline.co.zw/?s=",search,"&post_type=product&dgwt_wcas=1")
 
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = True

    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)
 
    # getting GeekForGeeks webpage
    driver.get(url)
    time.sleep(8)

    # add html to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    products = soup.find_all("div", {"class": "product"})
    # product__card mb-30 

    products_list = []
    for product in products:
        name = product.find("h3",{"class":"product-title"})
        if name is not None:
            name = name.text
        price = product.find("bdi")
        if price is not None:
            price = price.text
        image = ""
        if image is not None:
            image = product.find("a", {"title":""+name})


        #  if name is missing  dont add products
        if name != None:
            product = []
            # if image:
            #     image_url = image.get("style").split("(")[1].split(")")[0]  
            # else:
            #     image_url = None
            product.append(name)
            product.append(price)
            product.append(image)
            product.append("OK Supermarket")

            products_list.append(product)
        # print(products_list)

    # close browser after our manipulations
    driver.close()
    print(products_list)
    return products_list