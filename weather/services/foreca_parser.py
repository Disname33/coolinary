import json
import re

import requests
from bs4 import BeautifulSoup


def get_weather(city: str):
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
    weather_day = None
    if day_match:
        day_string = day_match.group(1)
        weather_day = json.loads(day_string)
        weather_day["daylen"] = f"{int(int(weather_day['daylen']) / 60)} ч {int(weather_day['daylen']) % 60} мин"
        weather_day["city"] = city
        # print(data[0]["uvi"])
        # for el in weather_day:
        #     print(el + ': ' + str(weather_day[el]))
    else:
        print("Данные 'dayForecast' не найдены в скрипте.")
    # Получение прогноза погоды на 5 дней с интервалом в 6 часов
    # Извлечение данных из объекта 'data'
    data_match = re.search(r'data:\s*(\[{.*}])', target_script8)
    weather_now = None
    data = None
    if data_match:
        data_string = data_match.group(1)
        data = json.loads(data_string)
        weather_now = data[0]
        weather_now["city"] = city
        # print(data[0])
        # for el in data:
        #     print(el + ': ' + str(data[el]))
    else:
        print("Данные 'data' не найдены в скрипте.")
    return weather_day, weather_now, data


def get_plot_coordinates(data):
    from datetime import datetime, timedelta
    timezone_offset = timedelta(hours=3)  # Смещение временной зоны +3 часа
    date = []
    temp = []
    if data is None:
        data = get_weather("Москва")[2]
    for data_per_6_hours in data:
        date.append(datetime.strptime(data_per_6_hours['time'], '%Y-%m-%dT%H:%M'))
        temp.append(data_per_6_hours['temp'])
    return date, temp


def get_uvi_day(city="Нижний Новгород"):
    return get_weather(city)[0]["uvi"]


def get_uvi_now(city="Нижний Новгород"):
    return get_weather(city)[1]["uvi"]


if __name__ == '__main__':
    get_weather("Нижний Новгород")
