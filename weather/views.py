from django.http import JsonResponse
from django.shortcuts import render

from .forms import CityForm
from .models import City
from .services.foreca_parser import get_weather, get_uvi_day, get_uvi_now, get_plot_coordinates
from .services.graf import plot_chart
from .services.open_weather_map import city_exist, get_weather_for_all_city


def weather(request):
    if name := request.GET.get('name'):
        if city_exist(name):
            City(name=name).save()
    form = CityForm()
    cities = City.objects.order_by('-date')[:6]
    weather_day, weather_now, data = get_weather(cities[0].name)
    x, y = get_plot_coordinates(data)
    context = {
        'weather_day': weather_day,
        'weather_now': weather_now,
        'plot': plot_chart(x=x, y=y,
                           x_label="Время", y_label="Температура",
                           title="График погоды"),
        'all_cities_info': get_weather_for_all_city(cities),
        'form': form
    }
    return render(request, 'weather/weather.html', context)


def uvi_day(request):
    city = "Нижний Новгород"
    if request.GET.get("city"):
        city = request.GET.get("city")
    uvi_value = get_uvi_day(city)
    data = {"status": "ok", "text": f"солнечное излучение в {city} днём {uvi_value} балл", "value": uvi_value}
    return JsonResponse(data)


def uvi_now(request):
    city = "Нижний Новгород"
    if request.GET.get("city"):
        city = request.GET.get("city")
    uvi_value = get_uvi_now(city)
    data = {"status": "ok", "text": f"солнечное излучение в {city} сейчас {uvi_value} балл", "value": uvi_value}
    return JsonResponse(data)
