import os
import time
import pandas as pd
from selenium import webdriver

#Функция подготовки блока страниц для парсинга, открытие страницы поиска и выставление фильтров, а также расчёт страниц
def search(driver, keyword):
    url = "https://elibrary.ru/querybox.asp?scope=newquery"
    driver.get(url)
    print("Waiting for load...")
    driver.find_element_by_tag_name('textarea').send_keys(keyword)
    time.sleep(1)
    driver.find_element_by_link_text('Поиск').click()
    time.sleep(15)
    num = int(driver.find_element_by_link_text('В конец').get_attribute("href").split("=")[1])
    if num > 100:
        num = 100
    print("Total " + str(num) + " pages for " + str(keyword))
    return num

#Функция перехода на следующую страницу
def next_page(driver):
    script = driver.find_element_by_link_text('>>').get_attribute("href")
    driver.get(script)
    time.sleep(10)

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
    return res

#Параметры парсера
keyword = "энергетика"                  #Используется в фильтре как ключевое слово, по которому будет происходить парсинг
res_dir = "Result"                      #Путь до папки для сохранения результатов (по стандарту создаётся папка Result)

if not os.path.exists(res_dir):
    os.mkdir(res_dir)

#Открываем сайт и ждём
driver = webdriver.Chrome("Driver/chromedriver.exe")

#Работа парсера
n = search(driver, keyword)
res = open(driver, n, keyword)

keyword = "водород"
n = search(driver, keyword)
res = open(driver, n, keyword)
