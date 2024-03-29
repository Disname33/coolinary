from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_gpt, name='chat_gpt'),
    path('chat/', views.chat_gpt_original, name='chat_gpt_original'),
    path('chat/<conversation_id>', views.chat_gpt_original, name='chat_gpt_original'),
    path('conversation', views.conversation),
    path('backend-api/v2/models', views.get_models),
    path('backend-api/v2/providers', views.get_providers),
    path('backend-api/v2/conversation', views.handle_conversation),
    path('backend-api/v2/gen.set.summarize:title', views.generate_title),
    path('backend-api/v2/error', views.handle_error),
]
