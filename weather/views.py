import requests
from django.http import JsonResponse
from django.shortcuts import render

from coolinary.secret.secret import openweathermap_api_key
from .forms import CityForm
from .models import City


def weather(request):
    if request.method == 'GET':
        form = CityForm(request.GET)
        form.save()
    form = CityForm()
    api_key = openweathermap_api_key
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&appid={}'
    cities = City.objects.order_by('-id')[:10]
    all_cities = []
    for city in cities:
        res = requests.get(url.format(city.name, api_key)).json()
        city_info = {
            'city': res['name'],
            'temp': res["main"]['temp'],
            'icon': res['weather'][0]['icon']
        }
        all_cities.append(city_info)

    context = {
        'all_cities_info': all_cities,
        'form': form
    }
    return render(request, 'weather/weather.html', context)


def uf(request):
    data = {"status": "ok", "text": "солнечное излучение 1 балл", "value": "1"}
    return JsonResponse(data)
