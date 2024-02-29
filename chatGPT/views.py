import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .services.chatGPT import get_welcome_message
from .services.gpt4free import create_image, get_response


@login_required
def chat_gpt(request):
    if json_data := request.POST.get('chat-message-input'):
        messages = json.loads(json_data)
        return HttpResponse(get_response(messages))
    elif image_prompt := request.POST.get('image_prompt'):
        print(image_prompt)
        image_url = create_image(image_prompt)
        return HttpResponse(image_url)
    return render(request, 'chatGPT/room.html', {"welcome": get_welcome_message()})
