#Загрузка для парсера

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd

#Загрузка библиотек для токинайзера

from tqdm.notebook import tqdm
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
browser = webdriver.Chrome("Driver/chromedriver.exe")

titles = []

#Выгрузка массива данных по статьям

for num in range(0,901,100):
    url = 'https://www.sciencedirect.com/search?qs=hydrogen%20energy&years=2019%2C2020%2C2021&show=100&sortBy=date&offset=' + str(num)
    browser.get(url)
    time.sleep(5)
    page = browser.page_source
    soup = BeautifulSoup(page)
    inf_1 = soup.findAll('div', {'class':'result-item-content'})
    inf_2 = [unit.find('h2').text for unit in inf_1]
    titles.extend(inf_2)

#Настройки токинайзера
stop_words = stopwords.words('english')

col_names = ['Название статьи']
df = pd.DataFrame(list(titles))
df.columns = col_names

noun = ['NNS', 'VBZ', 'NN', 'NNP']
verb = ['VBG', 'VBP', 'VBN', 'VBD', 'VB']
adj = ['JJ', 'JJR']

tokkens_final_list = []
tokkens_final_count_list = []
tokkens_full_final_list = []

#Токенизация
print('Токенизация первичной информации')
for text in tqdm(titles):
    text_1 = re.sub(r'[^\w\s\d]', '', text)
    if len(text_1.strip()) > 10:
        tokkens_list = word_tokenize(text_1.lower())
        tokkens_tag_list = pos_tag(tokkens_list)
        tokkens_lem_list = []
        for element in tokkens_tag_list:
            if element[1] in noun:
                tokkens_lem_list.append(WordNetLemmatizer().lemmatize(element[0], pos = 'n'))
            elif element[1] in verb:
                tokkens_lem_list.append(WordNetLemmatizer().lemmatize(element[0], pos = 'v'))
            elif element[1] in adj:
                tokkens_lem_list.append(WordNetLemmatizer().lemmatize(element[0], pos = 'a'))
        tokkens_final = []
        for element in tokkens_lem_list:
            if element not in stop_words:
                tokkens_final.append(element)
        tokkens_final_list.append(tokkens_final)
        tokkens_full_final_list.extend(tokkens_final)
        tokkens_final_count_list.append(len(tokkens_final))
    else:
        tokkens_final_list.append([])
        tokkens_final_count_list.append(0)

df['Токены'] = tokkens_final_list
df['Количество токенов'] = tokkens_final_count_list
df.to_excel('токеннизированный_массив_естественной_информации.xlsx')