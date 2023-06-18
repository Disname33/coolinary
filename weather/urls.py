from django.urls import path

from . import views

urlpatterns = [
    path('', views.weather, name='weather'),
    path('uvi', views.uvi_now, name='uvi'),
    path('uvi_day', views.uvi_day, name='uvi_day'),
    path('uvi_now', views.uvi_now, name='uvi_now'),
    path('all_data', views.all_data, name='all_data'),

]
