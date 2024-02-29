from django.urls import path

from . import views

urlpatterns = [
    path('', views.fool, name='card_games'),
    path('fool/<int:pk>/', views.fool, name='fool')
]
