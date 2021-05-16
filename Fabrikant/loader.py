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
            date.append(str(bgn.strftime("%d.%m.%Y")))
            date.append(str(today.strftime("%d.%m.%Y")))
            period.append(date)
            break
        date.append(str(bgn.strftime("%d.%m.%Y")))
        date.append(str(fnl.strftime("%d.%m.%Y")))
        period.append(date)
    return period

def date_transform(date_string):
    date_list = date_string.split(" ")
    dictionary = ["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"]
    for month in range(1,len(dictionary)+1):
        if date_list[1] == dictionary[month-1]:
            date_list[1] = month
    date_tr = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
    return str(date_tr.strftime("%d.%m.%Y"))

def data_filter(driver,load_date):
    #Очистка
    driver.find_element_by_id('drop_all_filters').click()
    #Новые значения
    print("Loadind date filter...")
    date_min = driver.find_element_by_id('date_from')
    date_min.send_keys(load_date[0])
    date_max = driver.find_element_by_id('date_to')
    date_max.send_keys(load_date[1])
    time.sleep(1)

def keyword_filter(driver, keyword):
    #Очистка
    driver.find_element_by_class_name('clear_form').click()
    #Новые значения
    search = driver.find_element_by_id('search_query')
    search.send_keys(keyword)
    time.sleep(1)

def opener(driver,load_date,keyword=None):
    data_filter(driver,load_date)
    if not keyword == None:
        keyword_filter(driver, keyword)

    driver.find_element_by_id('search_submit').click()
    time.sleep(2)
    buttons = driver.find_elements_by_xpath(".//li[@class='pagination__lt__el']")
    n = 0
    if len(buttons) > 0:
        n = buttons[len(buttons)-1].text
    if int(n) > 0:
        print("Number of pages is " + str(n))
    return n

def next_page(driver):
    driver.find_element_by_xpath('.//a[@class="pagination__nav-btn pagination__nav-btn_active pagination__link"]').click()
    time.sleep(5)

def page_parser(driver):
    order = []
    page = []
    purch = driver.find_elements_by_class_name('marketplace-unit__title')
    org = driver.find_elements_by_class_name('marketplace-unit__organizer')
    prc = driver.find_elements_by_class_name('marketplace-unit__price')
    deal = driver.find_elements_by_class_name('marketplace-unit__state__wrap')
    for i in range(0, len(purch)):
        order.append(purch[i].text)
        order.append(org[i].text.replace('Организатор:', ''))
        if prc[i].text[0] == 'У' or prc[i].text[0] == 'Ц':
            order.append("")
        else:
            order.append(prc[i].find_element_by_css_selector('strong').text.replace(' ',''))
        order.append(date_transform(deal[i].find_elements_by_class_name('marketplace-unit__state')[-1].find_element_by_class_name('dt').text))
        page.append(order)
        order = []
    if page == []:
        print("Nothing is parsed")
    return page

def parse(driver, n, date_interval, autosave=10, keyword = "All"):
    res = []
    #Проверка на наличие папок
    dirpath = "Database/" + str(keyword) + "/Data/"
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    if not os.path.exists(dirpath + str(date_interval[0]) + "/"):
        os.mkdir(dirpath + str(date_interval[0]) + "/")
    print("Parsing batch...")
    if n == 0:
        res = page_parser(driver)
        df = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price', 'Date'])
        df.to_csv(dirpath + str(date_interval[0]) + "/1.csv", sep=";", encoding="utf-8")
        print("Attempt to parse a single page")
    #Цикл парсинга страниц по заданному параметрам во времени и ключевому слову
    for count in range(1, int(n)+1):
        print("Now parsing " + str(count) + " page...")
        page = page_parser(driver)
        res.extend(page)
        if count == n:
            print("End of parsing batch. Saving...")
            df = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price', 'Date'])
            df.to_csv(dirpath + str(date_interval[0]) + "/" + str(count) + ".csv", sep=";", encoding="utf-8")
            break
        #Автосейвы по страницам
        if count % autosave == 0:
            df = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price', 'Date'])
            df.to_csv(dirpath + str(date_interval[0]) + "/" + str(count) + ".csv", sep=";", encoding="utf-8")
        next_page(driver)
    print("Total units parsed: " + str(len(res)))
    return res

#Ссылка на вэбдрайвер для селениума и ссылка на сайт для парсинга
driver = webdriver.Chrome("Driver/chromedriver.exe")
url = "https://www.fabrikant.ru/trades/procedure/search/?type=0&org_type=org&currency=0&date_type=date_publication&ensure=all&okpd2_embedded=1&okdp_embedded=1&count_on_page=20&order_direction=1&active=0&type_hash=1561441166"

#Параметры парсера
keyword = "энергетика"                  #Передать None, чтобы расчёт не включал в себя ключевое слово
autosave = 10                           #Стандартное значение 10 страниц для автосейва
dates = date_parser(9,50)               #Массив (n,m) для расчёта на n лет с разбиением по m дней
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
    pgs = opener(driver, interval, keyword)
    result.extend(parse(driver, pgs, interval, autosave, keyword,))
    df = pd.DataFrame(result, columns=['Purchase', 'Organisation', 'Price', 'Date'])
    df.to_csv(res_dir + "/Result/Result.csv", sep=";", encoding="utf-8")
    df.to_excel(res_dir +"/Result/Result.xlsx")

print("End of parsing")
driver.close()