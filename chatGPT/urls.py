from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_gpt, name='chat_gpt'),
    path('original', views.chat_gpt_original, name='chat_gpt_original'),
    path('conversation', views.conversation),
    # path('backend-api/v2/conversation', views.conversation),
]
