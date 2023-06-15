import json
import re

import requests
from bs4 import BeautifulSoup

city = "Моршанск"
url = "https://www.foreca.ru/Russia/" + city
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")
target_script7 = str(soup.find_all('script')[7])[8:-8]
target_script8 = str(soup.find_all('script')[8])[8:-8]
# Извлечение содержимого скрипта
# script_content = re.search(r'<script>(.*?)</script>', str(target_script), re.DOTALL).group(1)
# Получение прогноза погоды на сегодня
# Извлечение данных из объекта 'dayForecast'
day_match = re.search(r'dayForecast:\s*({.*})', target_script7)
if day_match:
    day_string = day_match.group(1)
    day = json.loads(day_string)
    # print(data[0]["uvi"])
    # for el in day:
    #     print(el + ': ' + str(day[el]))
else:
    print("Данные 'dayForecast' не найдены в скрипте.")
# Получение прогноза погоды на 5 дней с интервалом в 6 часов
# Извлечение данных из объекта 'data'
data_match = re.search(r'data:\s*(\[{.*}])', target_script8)
if data_match:
    data_string = data_match.group(1)
    data = json.loads(data_string)
    # print(data[0]["uvi"])
    # for hours in data:
    #     print(hours)
else:
    print("Данные 'data' не найдены в скрипте.")
