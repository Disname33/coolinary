import uuid
from time import time

from django.http import HttpRequest
from django.shortcuts import render, redirect


class Website:
    def __init__(self, url_prefix) -> None:
        self.url_prefix = url_prefix

    def _chat(self, request: HttpRequest, conversation_id):
        if '-' not in conversation_id:
            return redirect('._index')

        return render(request, 'chatGPT/GPT_style_room.html',
                      {'chat_id': conversation_id, 'url_prefix': self.url_prefix})

    def _index(self, request: HttpRequest):
        return render(request, 'chatGPT/GPT_style_room.html', {
            'chat_id': f'{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{hex(int(time() * 1000))[2:]}',
            'url_prefix': self.url_prefix})
