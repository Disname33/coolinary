"""
URL configuration for coolinary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('chat/', include('chat.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('profile/', views.profile, name='profile'),
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('admin/', admin.site.urls),
    path('games/', include('games.urls'), name='games'),
    path('game/', include('guess_the_word_game.urls'), name='guess_the_word'),
    path('guess_the_word/', include('guess_the_word_game.urls'), name='start_guess_the_word_game'),
    path('weather/', include('weather.urls'), name='weather'),
    path('register/', views.register, name='register'),
    path('device-info/', views.device_info, name='device_info'),
]
