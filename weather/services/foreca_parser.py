import json
import re

import requests
from bs4 import BeautifulSoup


def get_weather(city: str):
    url = "https://www.foreca.ru/Russia/" + city
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    scripts = soup.find_all('script')
    # print(*scripts, sep="\n\n\n")
    # target_script7 = str(scripts[8])[8:-8]
    # target_script8 = str(scripts[9])[8:-9]
    observations_script = next((str(script)[8:-9] for script in scripts if str(script)[52:64] == "Observations"), None)
    data_script = next((str(script)[8:-9] for script in scripts if str(script)[48:68] == "AirPressureMeteogram"), None)
    # Извлечение содержимого скрипта
    # script_content = re.search(r'<script>(.*?)</script>', str(target_script), re.DOTALL).group(1)
    # Получение прогноза погоды на сегодня
    # Извлечение данных из объекта 'dayForecast'
    obs = re.search(r'obs:\s*(\[{.*}])', observations_script)
    weather_now = None
    if obs:
        weather_now = json.loads(obs.group(1))[0]
        weather_now["city"] = city
        # print(now)
        # for el in now[0]:
        #     print(el)
    else:
        print("Данные 'obs' не найдены в скрипте.")

    day_forecast = re.search(r'dayForecast:\s*({.*})', observations_script)
    weather_day = None
    if day_forecast:
        weather_day = json.loads(day_forecast.group(1))
        weather_day["daylen"] = f"{int(int(weather_day['daylen']) / 60)} ч {int(weather_day['daylen']) % 60} мин"
        weather_day["city"] = city
        # print(data[0]["uvi"])
        # for el in weather_day:
        #     print(el + ': ' + str(weather_day[el]))
    else:
        print("Данные 'dayForecast' не найдены в скрипте.")
    # Получение прогноза погоды на 5 дней с интервалом в 6 часов
    # Извлечение данных из объекта 'data'
    data_match = re.search(r'data:\s*(\[{.*}])', data_script)
    data = None
    if data_match:
        data = json.loads(data_match.group(1))
        data[0]["city"] = city
        weather_now.update({key: data[0][key] for key in ("rainin", "uvi", "maxwindkmh")})
    else:
        print("Данные 'data' не найдены в скрипте.")
    return weather_day, data, weather_now


def get_plot_coordinates(data):
    from datetime import datetime
    date = []
    temp = []
    uvi = []
    rain = []
    if data is None:
        data = get_weather("Москва")[1]
    for data_per_6_hours in data:
        date.append(datetime.strptime(data_per_6_hours['time'], '%Y-%m-%dT%H:%M'))
        temp.append(data_per_6_hours['temp'])
        rain.append(data_per_6_hours['rain'])
        if data_per_6_hours['uvi']:
            uvi.append(data_per_6_hours['uvi'])

    return date, temp, uvi, rain


def get_uvi_day(city="Нижний Новгород"):
    return get_weather(city)[0]["uvi"]


def get_uvi_now(city="Нижний Новгород"):
    return get_weather(city)[1][0]["uvi"]


if __name__ == '__main__':
    get_weather("Нижний Новгород")
