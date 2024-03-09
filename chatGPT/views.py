import json
import uuid
from time import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.chatGPT import get_welcome_message
from .services.gpt4free import create_image, get_response
from .services.server import babel
from .services.server.backend import Backend_Api


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


def chat_gpt_original(request):
    return render(request, 'chatGPT/GPT_style_room.html', {
        'chat_id': f'{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{hex(int(time() * 1000))[2:]}'})


@csrf_exempt
def conversation(request):
    return Backend_Api.conversation(request)


def get_languages(request):
    return babel.get_languages(request)


def get_locale(request):
    return babel.get_locale(request)


@csrf_exempt
def change_language(request):
    request.session['language'] = request.POST.get('language')
    request.session.save()
    return JsonResponse({}, status=204)
