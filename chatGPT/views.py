import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .services.chatGPT import get_last_message_from_response, get_welcome_message_and_update


@login_required
def chat_gpt(request):
    if json_data := request.POST.get('chat-message-input'):
        messages = json.loads(json_data)
        return HttpResponse(get_last_message_from_response(messages))
    return render(request, 'chatGPT/room.html', {"welcome": get_welcome_message_and_update()})
