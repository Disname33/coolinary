import requests

from coolinary.secret.secret import openweathermap_api_key


def city_exist(city: str) -> bool:
    try:
        res = requests.get("https://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': openweathermap_api_key})
        data = res.json()
        city_id = data['list'][0]['id']
        return city_id
    except Exception as e:
        print("Exception (find):", e)
        return False


def get_weather_for_all_city(cities) -> []:
    all_cities = []
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&appid={}'
    try:
        for city in cities:
            res = requests.get(url.format(city.name, openweathermap_api_key))
            data = res.json()
            city_info = {
                'city': data['name'],
                'temp': data["main"]['temp'],
                'icon': data['weather'][0]['icon']
            }
            all_cities.append(city_info)
        return all_cities
    except Exception as e:
        print("Exception (find):", e)
        return all_cities
