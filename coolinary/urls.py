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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('chat/', include('chat.urls'), name='chat_main'),
    path('chatGPT/', include('chatGPT.urls'), name='chatGPT_main'),
    path('accounts/login/', views.secure_login_view, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name='profile'),
    # path('profile/', views.profile, name='profile'),
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('admin/', admin.site.urls, name='admin_panel'),
    path('games/', include('games.urls'), name='games'),
    path('game/pole_chudes/', include('pole_chudes.urls'), name='pole_chudes_game'),
    path('game/guess_the_word/', include('guess_the_word_game.urls'), name='guess_the_word'),
    path('guess_the_word/', include('guess_the_word_game.urls'), name='start_guess_the_word_game'),
    path('game/', include('games.urls'), name='game'),
    path('weather/', include('weather.urls'), name='weather'),
    path('register/', views.register, name='register'),
    path('device-info/', views.device_info, name='device_info'),
    path('debt/', include('debt_app.urls'), name='debt'),
    path('familytree/', include('familytree.urls'), name='familytree'),
    path('i18n/', include('django.conf.urls.i18n'), name='lang'),
]
# urlpatterns += i18n_patterns(
#     path('chatGPT/', include('chatGPT.urls')),
# )
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
