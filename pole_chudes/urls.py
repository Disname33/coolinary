from django.urls import path

from . import views

urlpatterns = [
    path('room/<int:pk>/', views.room, name='pole_chudes'),
    path('', views.lobby, name='pole_chudes_lobby'),
]
