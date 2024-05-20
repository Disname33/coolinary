import json
import logging

from channels.generic.websocket import WebsocketConsumer
from g4f import get_last_provider, ChatCompletion
from g4f import models
from g4f.gui.server.api import conversations
from g4f.gui.server.config import special_instructions
from g4f.gui.server.internet import get_search_message
from g4f.image import to_image, ImagePreview
from g4f.providers.base_provider import FinishReason
from g4f.providers.conversation import BaseConversation

from chatGPT.services.gpt4free import set_all_cookies
from coolinary.services.image_crop import decode64
from .services.backend import get_error_message


class ChatGPTConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.send_json('message', 'Соединение с сервером разорвано!')

    def _create_response_stream(self, kwargs: dict):
        try:
            provider = kwargs.get('provider')
            conversation_id = kwargs.get('conversation_id')
            first = True
            for chunk in ChatCompletion.create(**kwargs):
                if chunk:
                    if first:
                        first = False
                        self.send_json('provider', get_last_provider(True))
                    if isinstance(chunk, BaseConversation):
                        if provider not in conversations:
                            conversations[provider] = {}
                        conversations[provider][conversation_id] = chunk
                        self.send_json("conversation", conversation_id)
                    elif isinstance(chunk, Exception):
                        logging.exception(chunk)
                        self.send_json("message", get_error_message(chunk))
                    elif isinstance(chunk, ImagePreview):
                        self.send_json("preview", chunk.to_string())
                    elif not isinstance(chunk, FinishReason):
                        self.send_json("content", str(chunk))
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
        provider = json_data.get('provider')

        if "image" in kwargs and not provider:
            provider = "Bing"
        if provider == 'OpenaiChat':
            kwargs['auto_continue'] = True

        messages = json_data['messages']

        if jailbreak := json_data.get('jailbreak', ''):
            messages = special_instructions.get(jailbreak, '') + messages
        model = json_data.get('model') or models.default
        # patch = patch_provider if json_data.get('patch_provider') else None
        api_key = json_data.get("api_key")
        if api_key is not None:
            kwargs["api_key"] = api_key
        if json_data.get('web_search'):
            if provider in ("Bing", "HuggingChat"):
                kwargs['web_search'] = True
            else:
                messages[-1]["content"] = get_search_message(messages[-1]["content"])

        conversation_id = json_data.get("conversation_id")
        if conversation_id and provider in conversations and conversation_id in conversations[provider]:
            kwargs["conversation"] = conversations[provider][conversation_id]
        return {
            "model": model,
            "provider": provider,
            "messages": messages,
            "stream": True,
            "ignore_stream": True,
            "return_conversation": True,
            'conversation_id': conversation_id,
            **kwargs
        }
