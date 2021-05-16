import os
import time
import datetime
import pandas as pd
from selenium import webdriver

#Функция разбиения по времени для парсера
#years - число лет для расчёта от текущей даты
#days - шаг разбиения в днях
def date_parser(years = 5, days = 2):
    begin = datetime.date(datetime.date.today().year-years,datetime.date.today().month,datetime.date.today().day)
    today = datetime.date.today()
    distance = (today - begin).days
    iterations = distance // days
    fnl = begin
    period = []
    #Условаие на неровное разбиение по интервалам
    if not distance % days == 0:
        iterations += 1
    #Заполнение массива интервалов
    for cut in range(iterations):
        date = []
        bgn = fnl
        fnl = bgn + datetime.timedelta(days=days)
        #Условие поиска последнего интервала
        if cut == iterations - 1:
            date.append(str(bgn.strftime("%d.%m.%Y") + " 00:00"))
            date.append(str(today.strftime("%d.%m.%Y") + " 00:00"))
            period.append(date)
            break
        date.append(str(bgn.strftime("%d.%m.%Y") + " 00:00"))
        date.append(str(fnl.strftime("%d.%m.%Y") + " 00:00"))
        period.append(date)
    return period

#Вписывание значений даты и очистка фильтра целиком
#data - list[n,m], где n - начальная дата, m - конечная дата. Формат даты [dd.mm.yyyy hh:mm:ss]
def data_filter(driver,data):
    #Открытие фильтра
    container = driver.find_element_by_id("specialFilters")
    driver.execute_script("arguments[0].style.display = 'block';", container)
    #Очистка
    time.sleep(3)
    driver.find_element_by_xpath(".//input[@value='Сброс']").click()
    #Поиск и заполнение полей дат
    print("Writing dates...")
    min = driver.find_element_by_id("PublicDateMin")
    max = driver.find_element_by_id("PublicDateMax")
    min.send_keys(data[0])
    max.send_keys(data[1])
    time.sleep(1)
    return

#Функция записи ключевого слова в поисковую строку
def keyword_filter(driver,keyword):
    #Очистка
    time.sleep(3)
    driver.find_element_by_xpath(".//button[@id='searchClear']").click()
    print("Writing keyword...")
    box = driver.find_element_by_xpath(".//input[@placeholder='Введите ключевые слова или номер процедуры']")
    box.send_keys(keyword)

#Функция поиска по ключевому слову и открытия первой страницы массива для парсинга
def opener(driver,keyword=None,date=None):
    #Проверка на поиск по ключевым словам
    if not keyword==None:
        keyword_filter(driver,keyword)
    #Подгрузка временного интервала и запуск поиска страниц для парсинга
    data_filter(driver,date)
    search = driver.find_element_by_xpath(".//button[@class='mainSearchBar-find']")
    search.click()
    time.sleep(4)
    #Поиск последний страницы через кнопку перехода к последней странице
    buttons = driver.find_elements_by_xpath(".//span[@class='pager-button pagerElem']")
    n = 0
    for btn in buttons:
        if btn.text == '>>':
            n = btn.get_attribute("content")
            break
    if int(n) > 0:
        print("Number of pages is " + str(n))
    return n

# Функция парсинга страницы, выгружающая тендер, компанию, цену и дату
def page_parser(driver):
    page = []
    order = []
    purch = driver.find_elements_by_class_name('es-el-name')
    org = driver.find_elements_by_class_name('es-el-org-name')
    prc = driver.find_elements_by_class_name('es-el-amount')
    dt = driver.find_elements_by_xpath(".//span[@content='leaf:EndDate']")
    for i in range(0, len(purch)):
        order.append(purch[i].text)
        order.append(org[i].text)
        order.append(prc[i].text.replace(' ',''))
        order.append(dt[i].text)
        page.append(order)
        order = []
    return page

#Функция перехода на следующую страницу через поиск кнопки
def next_page(driver):
    buttons = driver.find_elements_by_id('pageButton')
    for btn in buttons:
        if btn.text == '>  ':
            btn.find_elements_by_xpath(".//span[@class='pager-button pagerElem']")[0].click()
            break
    time.sleep(5)
    return

#Функция парсинга всего массива исходя из первоначальных условий
def parse(driver, n, date_interval, autosave=10, keyword = "All"):
    res = []
    #Проверка на наличие папок
    dirpath = "Database/" + str(keyword) + "/Data/"
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    if not os.path.exists(dirpath + str(date_interval[0].split(" ")[0]) + "/"):
        os.mkdir(dirpath + str(date_interval[0].split(" ")[0]) + "/")

    #Цикл парсинга страниц по заданному параметрам во времени и ключевому слову
    for count in range(1, int(n)+1):
        print("Now parsing " + str(count) + " page...")
        page = page_parser(driver)
        res.extend(page)
        if count == n:
            print("End of parsing. Saving...")
            df = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price', 'Date'])
            df.to_csv(dirpath + str(date_interval[0].split(" ")[0]) + "/" + str(count) + ".csv", sep=";", encoding="utf-8")
            break
        #Автосейвы по страницам
        if count % autosave == 0:
            df = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price', 'Date'])
            df.to_csv(dirpath + str(date_interval[0].split(" ")[0]) + "/" + str(count) + ".csv", sep=";", encoding="utf-8")
        next_page(driver)
    print("Total units parsed: " + str(len(res)))
    return res

#Драйвер и ссылка на сайт
driver = webdriver.Chrome("Driver/chromedriver.exe")
url = 'https://www.sberbank-ast.ru/UnitedPurchaseList.aspx'

#Параметры парсера
keyword = "энергетика"                  #Передать None, чтобы расчёт не включал в себя ключевое слово
autosave = 10                           #Стандартное значение 10 страниц для автосейва
dates = date_parser(1,100)              #Массив (n,m) для расчёта на n лет с разбиением по m дней
result = []                             #Массив итоговых значений по выгрузке

#Открываем сайт и ждём
driver.get(url)
print("Waiting for load...")
time.sleep(5)

#Проверка и создание папок куда будет скидываться готовый результат
res_dir = "Database/" + str(keyword)
if not os.path.exists(res_dir):
    os.mkdir(res_dir)
if not os.path.exists(res_dir + "/Result/"):
    os.mkdir(res_dir + "/Result/")
#Массив перебора всех интервалов с условием на отсутствие данных для некоторых интервалов. Сохранение итогового массива.
for interval in dates:
    pgs = 0
    pgs = opener(driver, keyword, interval)
    if not pgs == 0:
        result.extend(parse(driver, pgs, interval, autosave, keyword,))
        df = pd.DataFrame(result, columns=['Purchase', 'Organisation', 'Price', 'Date'])
        df.to_csv(res_dir + "/Result/Result.csv", sep=";", encoding="utf-8")
        df.to_excel(res_dir +"/Result/Result.xlsx")
    else:
        print("Nothing to parse here D:")

driver.close()