from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_gpt, name='chat_gpt'),
    path('original', views.chat_gpt_original, name='chat_gpt_original'),
    # path('get-languages', views.get_languages),
    # path('get-locale', views.get_locale),
    path('conversation', views.conversation),
    # path('backend-api/v2/conversation', views.conversation),
    path('change-language', views.change_language),
]
