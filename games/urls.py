from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.games, name='games'),
    path('tetris', views.tetris, name='tetris'),
    path('tetris-results', views.tetris_results, name='tetris_results'),
    path('match-three', views.match_three, name='match_three'),
    path('match-three-results', views.match_three_results, name='match_three_results'),
    path('card/', include('card_games.urls')),
]
