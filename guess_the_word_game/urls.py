from django.urls import path

from . import views

urlpatterns = [
    path('', views.process_input, name='guess_the_word_game'),
    path('results', views.results, name='guess_the_word_game_results'),
    path('remove', views.remove, name='guess_the_word_game_remove'),
    path('helper', views.helper, name='guess_the_word_game_help'),
]
