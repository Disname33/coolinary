from django.urls import path

from . import views

urlpatterns = [
    path('', views.weather, name='weather'),
    path('uf', views.uf, name='uf'),

]
