from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import dateparser
import csv
import os
from datetime import datetime

# Настройки для веб-драйвера selenium
options = Options()
options.add_argument("--headless")

# Запрашиваем у пользователя входные данные
url = input("Введите ссылку на каталог для парсинга: ")
min_price = int(input("Введите минимальную цену: "))
max_price = int(input("Введите максимальную цену: "))

# Получаем название каталога из URL
catalog_name = url.split("/")[-1].replace("-", "_")  # Заменяем дефисы на подчеркивания

# Получаем текущую дату в формате ГГГГ-ММ-ДД
current_date = datetime.now().strftime("%Y-%m-%d")

# Создаем директорию result, если она не существует
os.makedirs("result", exist_ok=True)

# Имя файла
file_name = f"result/{catalog_name}_{current_date}.csv"

driver = webdriver.Firefox(options=options)
page = 1  # текущая страница, изначально 1

# Открываем файл
with open(file_name, 'w', encoding="utf-8", newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["id", "name", "price", "date"])

    # Пробегаемся по страницам
    while True:
        driver.get(url + str(page))

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        items = soup.find_all('div', attrs={'data-marker': 'item'})

        # Если на странице элементов нет, значит она последняя, дальше идти не нужно
        if len(items) == 0:
            break

        # Пробегаемся по элементам страницы
        for item in items:
            id = item.get("id")  # Идентификатор
            name = item.find('h3', attrs={"itemprop": "name"}).text.strip()  # Название
            price = item.find('meta', attrs={"itemprop": "price"})["content"]  # Цена

            # Парсим дату
            date = dateparser.parse(item.find('p', attrs={"data-marker": "item-date"}).text)

            # Если цена попадает в заданный промежуток, записываем в файл
            if min_price <= int(price) <= max_price:
                writer.writerow([id, name, price, date])

        page += 1

driver.quit()
