from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import datetime
import os  # Импортируем модуль os для работы с файловой системой
from fake_useragent import UserAgent, FakeUserAgentError

# Словарь для замены названий месяцев на числовые значения
dict_months = {
    "января": "1",
    "февраля": "2",
    "марта": "3",
    "апреля": "4",
    "мая": "5",
    "июня": "6",
    "июля": "7",
    "августа": "8",
    "сентября": "9",
    "октября": "10",
    "ноября": "11",
    "декабря": "12"
}

def parse(p: int = 1, base_url: str = ''):
    """Парсит данные с указанной страницы каталога товаров."""
    p = str(p)  # Преобразуем номер страницы в строку
    res = []  # Список для хранения результатов парсинга

    # Настройки для использования Firefox
    firefox_options = Options()

    firefox_options.add_argument("--headless")  # Можно раскомментировать для фона (без интерфейса)

    # Обработка пользовательского агента
    try:
        ua = UserAgent().random  # Генерация случайного пользовательского агента
    except FakeUserAgentError:
        # Если не удалось сгенерировать пользовательский агент, используем стандартный
        ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"

    # Установка пользовательского агента в настройки Firefox
    firefox_options.set_preference("general.useragent.override", ua)

    # Создаем экземпляр сервиса FirefoxDriver
    service = Service()  # Убедитесь, что geckodriver доступен в PATH
    # Инициализируем драйвер Firefox
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        # Переход на страницу с товарами
        driver.get(f'{base_url}?page={p}')  # Используем базовую ссылку и добавляем номер страницы
        try:
            # Ожидание, пока элементы товаров не появятся на странице
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card"))
            )
        except:
            return []  # Если товары не появились, возвращаем пустой список

        # Получение всех элементов с товарами
        cars = driver.find_elements(By.CSS_SELECTOR, '.product-card')  # Проверьте правильность селектора
        # Проходимся по всем предложениям
        for car in cars:
            buf = []  # Временный список для хранения данных о товаре
            buf.append(car.find_element(By.CSS_SELECTOR, ".product-card__link").get_attribute("href").split("/")[-2])  # ID товара
            buf.append(car.find_element(By.CSS_SELECTOR, '.product-card__name').text)  # Название товара
            buf.append(car.find_element(By.CSS_SELECTOR, '.price').text)  # Цена товара
            data = car.find_element(By.CSS_SELECTOR, '.btn-text').text  # Дата

            # Обработка даты
            date_processed = process_date(data)  # Преобразуем дату в нужный формат
            buf.append(date_processed)  # Добавляем обработанную дату в список
            res.append(buf)  # Добавляем данные о товаре в общий список результатов

    finally:
        driver.quit()  # Закрываем браузер, освобождая ресурсы

    return res  # Возвращаем результаты парсинга

def process_date(data: str) -> str:
    """Обрабатывает строку даты и возвращает дату в формате MM.DD.YY."""
    # Обработка даты
    if data == "Послезавтра":
        data = datetime.date.today() + datetime.timedelta(days=2)  # Дата послезавтра
    elif data == "Завтра":
        data = datetime.date.today() + datetime.timedelta(days=1)  # Дата завтра
    else:
        # Разделяем строку даты на составляющие
        arr = data.split()
        d = int(arr[0])  # День
        m = int(dict_months[arr[1]])  # Месяц
        a = datetime.datetime.today().year  # Текущий год
        # Если дата уже прошла, увеличиваем год на 1
        data = datetime.date(a, m, d) if datetime.datetime(a, m, d) > datetime.datetime.today() else datetime.date(a + 1, m, d)

    return data.strftime("%m.%d.%y")  # Форматируем дату в MM.DD.YY

def main():
    """Основная функция, запускающая парсинг и записывающая данные в файл."""
    base_url = input("Введите ссылку на страницу каталога товаров: ")  # Запрос ссылки у пользователя

    # Извлекаем название каталога из URL
    catalog_name = base_url.split('/')[-1] if base_url else 'catalog'
    catalog_name = catalog_name.replace(' ', '_')  # Заменяем пробелы на символы подчеркивания для имени файла

    result = []  # Список для хранения всех товаров
    n = 1  # Начинаем с первой страницы
    while True:
        buf = parse(n, base_url)  # Парсим данные с текущей страницы
        if not buf:  # Если данных нет, выходим из цикла
            break
        result += buf  # Добавляем все товары на странице в общий список
        n += 1  # Переход к следующей странице

    # Получаем текущее время и форматируем его
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Формируем имя файла
    filename = f"{catalog_name}_{current_time}.csv"

    # Убедитесь, что директория result существует
    if not os.path.exists('result'):
        os.makedirs('result')  # Создаем директорию, если она не существует

    # Открываем файл с указанием кодировки utf-8 и добавляем заголовки
    with open(os.path.join('result', filename), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)  # Создаем объект для записи в CSV
        # Записываем заголовки столбцов
        writer.writerow(["ID", "Название", "Цена", "Дата"])
        writer.writerows(result)  # Записываем данные о товарах

if __name__ == "__main__":
    main()  # Запускаем основную функцию
