from django.urls import path

from . import views

urlpatterns = [
    path('', views.games, name='games'),
    path('tetris', views.tetris, name='tetris'),
    path('tetris-results', views.tetris_results, name='tetris_results'),
]
