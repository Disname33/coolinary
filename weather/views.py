from django.http import JsonResponse
from django.shortcuts import render

from .forms import CityForm
from .models import City
from .services.open_weather_map import city_exist, get_weather_for_all_city


def weather(request):
    if name := request.GET.get('name'):
        if city_exist(name):
            City(name=name).save()
    form = CityForm()
    cities = City.objects.order_by('-date')[:10]
    context = {
        'all_cities_info': get_weather_for_all_city(cities),
        'form': form
    }
    return render(request, 'weather/weather.html', context)


def uf(request):
    data = {"status": "ok", "text": "солнечное излучение 1 балл", "value": "1"}
    return JsonResponse(data)
