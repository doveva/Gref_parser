from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
import pandas as pd


def main():
    # загурзка драйвера
    driver = webdriver.Chrome(executable_path="Driver/chromedriver.exe")
    try:
        driver.get(f"https://zakupki.rosatom.ru/Web.aspx?node=currentorders&ostate=P&page=1")
        # считаем кол-во страниц на сайте
        amount_pages = int(driver.find_element_by_xpath(
            '/html/body/form/div[4]/div[5]/div[2]/div[2]/div[2]/ul/li[8]/p').text)
        print(f'Total amount of pages {int(amount_pages)}')
        # Запуск таймера, для контроля времени работы
        start_time = time()
        # контейнер для запросов
        res = []
        for i in range(1, amount_pages + 1):
            # пробегаемся по всем страницам итератором
            driver.get(f"https://zakupki.rosatom.ru/Web.aspx?node=currentorders&ostate=P&page={i}")
            print(f'Parsing page number {i}...')
            sleep(1)
            # все заявки вшиты в тег <tr>
            purchases = driver.find_elements_by_tag_name('tr')
            for link in purchases:
                # игнорируем пустые строки  и заголовок
                if not link.get_attribute("style") and link.text and 'Наименование' not in link.text:
                    information = link.text.split('\n')
                    name = information[1]
                    price = information[2]
                    organisation = information[4]
                    publication_date = information[5]

                    res.extend([[name, organisation, price, publication_date]])
            # каждые 50 страниц выводим время работы
            if i % 50 == 0 and (i != 0):
                print(f'\n|Time passed {time() - start_time} sec.|\n')


    except NoSuchElementException as e:
        # если элемент не был найдет, то выводим имя предпоследней заявки и ошибку
        print(name)
        print(e)
    except Exception as e:
        # ловим иные ошибки с traceback
        print(e.with_traceback())
    finally:
        # в конечном счете сохраням информацию в csv и xlsx
        table = pd.DataFrame(res, columns=['Purchase', 'Organisation', 'Price, rub', 'Date'])
        table.to_csv(r'Database\result.csv', sep=';', encoding='UTF-8')
        table.to_excel(r'Database\result.xlsx')

        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
