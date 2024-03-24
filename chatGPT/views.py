import json
import uuid
from time import time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.backend import Backend_Api as Backend
from .services.chatGPT import get_welcome_message
from .services.gpt4free import create_image, get_response
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


@login_required
def chat_gpt_original(request, conversation_id=None):
    if conversation_id is None:
        conversation_id = f'{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{hex(int(time() * 1000))[2:]}'
    return render(request, 'chatGPT/GPT_style.html', {'chat_id': conversation_id})


@login_required
@csrf_exempt
def conversation(request):
    return Backend_Api.conversation(request)


@login_required
def get_models(request):
    return JsonResponse(Backend(request).get_models(), safe=False)


@login_required
def get_providers(request):
    return JsonResponse(Backend(request).get_providers(), safe=False)


@login_required
@csrf_exempt
def handle_conversation(request):
    return Backend(request).handle_conversation()


@login_required
@csrf_exempt
def generate_title(request):
    return JsonResponse(Backend(request).generate_title())


@login_required
@csrf_exempt
def handle_error(request):
    return JsonResponse(Backend(request).handle_error(), safe=False)
