import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
from fake_useragent import UserAgent

#Функция подготовки блока страниц для парсинга, открытие страницы поиска и выставление фильтров, а также расчёт страниц
def search(keyword):
    ua = UserAgent()
    ua.random
    opts = Options().add_argument("user-agent=" + str(ua))
    driver = webdriver.Chrome("Driver/chromedriver.exe", chrome_options=opts)
    url = "https://elibrary.ru/querybox.asp?scope=newquery"
    # Открываем сайт и ждём
    driver.get(url)
    print("Waiting for load...")
    time.sleep(random.randrange(2, 5))
    driver.find_element_by_tag_name('textarea').send_keys(keyword)
    driver.find_element_by_link_text('Поиск').click()
    time.sleep(random.randrange(5,30))
    num = int(driver.find_element_by_link_text('В конец').get_attribute("href").split("=")[1])
    if num > 100:
        num = 100
    print("Total " + str(num) + " pages for " + str(keyword))
    return num, driver

#Функция перехода на следующую страницу
def next_page(driver):
    script = driver.find_element_by_link_text('>>').get_attribute("href")
    driver.get(script)
    time.sleep(random.randrange(5,30))

#Функция парсинга страницы
def parse(driver):
    parsed_data = []
    titles = driver.find_elements_by_xpath(".//span[@style='line-height:1.0;']")
    for title in titles:
        parsed_data.append(title.text)
    return parsed_data

#Парсит подготовленный блок страниц
def open(driver, n, keyword, res_dir = "Result"):
    result = []

    for i in range(n):
        result.extend(parse(driver))
        print("Parsing " + str(i+1) + " page")
        if i==n-1:
            break
        next_page(driver)

    res = pd.DataFrame(result, columns=['Название статьи'])
    res.to_excel(res_dir + "/Result_" + str(keyword) + ".xlsx")
    print("End of parsing for " + str(keyword))
    driver.close()
    return res

#Параметры парсера
keywords = ["энергетика","водород"]                 #Используется в фильтре как ключевое слово, по которому будет происходить парсинг
res_dir = "Result"                      #Путь до папки для сохранения результатов (по стандарту создаётся папка Result)

if not os.path.exists(res_dir):
    os.mkdir(res_dir)

#Работа парсера

for keyword in keywords:
    search_res = search(keyword)
    n = search_res[0]
    driver = search_res[1]
    res = open(driver, n, keyword)

