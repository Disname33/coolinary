import json
import logging

from channels.generic.websocket import WebsocketConsumer
from g4f import get_last_provider, ChatCompletion
from g4f import models
from g4f.Provider.bing.create_images import patch_provider
from g4f.gui.server.config import special_instructions
from g4f.gui.server.internet import get_search_message
from g4f.image import to_image

from chatGPT.services.gpt4free import set_all_cookies
from coolinary.services.image_crop import decode64
from .services.backend import get_error_message


class ChatGPTConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.send_json('message', 'Соединение с сервером разорвано!')

    def _create_response_stream(self, kwargs):
        try:
            first = True
            for chunk in ChatCompletion.create(**kwargs):
                if chunk:
                    if first:
                        first = False
                        self.send_json('provider', get_last_provider(True))
                    if isinstance(chunk, Exception):
                        logging.exception(chunk)
                        self.send_json('message', get_error_message(chunk))
                    else:
                        self.send_json('content', str(chunk))
            self.send_json('finish', 'done')
        except Exception as e:
            logging.exception(e)
            self.send_json('error', get_error_message(e))

    def receive(self, text_data=None, bytes_data=None):
        kwargs = json.loads(text_data)
        self._create_response_stream(self._prepare_conversation_kwargs(kwargs))

    def send_json(self, message_type, data):
        return self.send(text_data=json.dumps({'type': message_type, 'data': data}))

    def _prepare_conversation_kwargs(self, data):
        kwargs = {}
        if file := data.get("image"):
            kwargs['image'] = to_image(decode64(file, 'png'), False)
            kwargs['image_name'] = 'image.png'
        if binary_json := data.get("json"):
            json_data = json.loads(binary_json)
        else:
            json_data = data
        set_all_cookies()
        provider = json_data.get('provider', '').replace('g4f.Provider.', '')
        provider = provider if provider and provider != "Auto" else None

        if "image" in kwargs and not provider:
            provider = "Bing"
        if provider == 'OpenaiChat':
            kwargs['auto_continue'] = True

        messages = json_data['messages']

        if jailbreak := json_data.get('jailbreak', ''):
            messages = special_instructions.get(jailbreak, '') + messages
        if json_data.get('web_search'):
            if provider == "Bing":
                kwargs['web_search'] = True
            else:
                # ResourceWarning: unclosed event loop
                messages[-1]["content"] = get_search_message(messages[-1]["content"])

        model = json_data.get('model')
        model = model if model else models.default
        patch = patch_provider if json_data.get('patch_provider') else None
        return {
            "model": model,
            "provider": provider,
            "messages": messages,
            "stream": True,
            "ignore_stream": True,
            "patch_provider": patch,
            **kwargs
        }
