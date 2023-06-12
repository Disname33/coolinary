from django.urls import path
from . import views


urlpatterns = [
    path('', views.process_input, name='guess_the_word_game'),
    path('results', views.results, name='guess_the_word_game_results'),
]
