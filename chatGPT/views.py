import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .services.chatGPT import get_last_message_from_response, get_welcome_message_and_update, create_image, moderation


@login_required
def chat_gpt(request):
    if json_data := request.POST.get('chat-message-input'):
        messages = json.loads(json_data)
        return HttpResponse(get_last_message_from_response(messages))
    elif image_prompt := request.POST.get('image_prompt'):
        print(moderation(image_prompt))
        image_url = create_image(image_prompt)
        return HttpResponse(image_url)
    return render(request, 'chatGPT/room.html', {"welcome": get_welcome_message_and_update()})
