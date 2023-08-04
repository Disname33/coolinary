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
    weather_day, data, weather_now = get_weather(cities[0].name)
    time, temp, uvi, rain = get_plot_coordinates(data)
    context = {
        'weather_day': weather_day,
        'weather_now': weather_now,
        'plot_temp': plot_chart(x=time, y=temp,
                                x_label="Дата", y_label="Температура, °C",
                                title=cities[0].name + ". График температуры", color='red', plot_type='plot'),
        'plot_uvi': plot_chart(x=time[:len(uvi)], y=uvi,
                               x_label="Дата", y_label="УФ-индекс",
                               title=cities[0].name + ". График УФ-излучения", color='violet', plot_type='plot'),
        'plot_rain': plot_chart(x=time, y=rain,
                                x_label="Дата", y_label="Осадки, мм",
                                title=cities[0].name + ". График осадков", color='blue', plot_type='bar'),
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


def all_data(request):
    city = "Нижний Новгород"
    if request.GET.get("city"):
        city = request.GET.get("city")
    data = {"status": "ok", "city": city, 'data': get_weather(city)[1]}
    return JsonResponse(data)
