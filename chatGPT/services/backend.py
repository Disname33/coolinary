import json
import logging
from typing import Generator

from django.core.handlers.wsgi import WSGIRequest
from django.http import StreamingHttpResponse
from g4f import ChatCompletion
from g4f import models
from g4f.Provider import __providers__
from g4f.client.service import get_last_provider
from g4f.gui.server.internet import get_search_message
from g4f.image import is_allowed_extension, to_image

from chatGPT.services.gpt4free import set_all_cookies
from coolinary.services.image_crop import decode64


class Backend_Api:

    def __init__(self, request: WSGIRequest) -> None:

        self.request = request

    def handle_error(self):
        print(self.request.body)
        return 'ok', 200

    def get_models(self):
        return list(models.ModelUtils.convert.keys())

    def get_providers(self):
        return [provider.__name__ for provider in __providers__ if provider.working]

    def generate_title(self):
        return {'title': ''}

    def handle_conversation(self):
        kwargs = self._prepare_conversation_kwargs()

        response = StreamingHttpResponse(streaming_content=self._create_response_stream(kwargs), )
        response['Transfer-Encoding'] = 'chunked'
        return response

    def _prepare_conversation_kwargs(self):
        """
        Prepares arguments for chat completion based on the request data.

        Reads the request and prepares the necessary arguments for handling
        a chat completion request.

        Returns:
            dict: Arguments prepared for chat completion.
        """
        kwargs = {}
        if file := self.request.FILES.get("image"):
            if file.filename != '' and is_allowed_extension(file.filename):
                kwargs['image'] = to_image(decode64(file, '.svg'), file.filename.endswith('.svg'))
                kwargs['image_name'] = file.filename
        if binary_json := self.request.POST.get("json"):
            json_data = json.loads(binary_json)
        else:
            json_data = json.loads(self.request.body)
        set_all_cookies()
        provider = json_data.get('provider', '').replace('g4f.Provider.', '')
        provider = provider if provider and provider != "Auto" else None

        if "image" in kwargs and not provider:
            provider = "Bing"
        if provider == 'OpenaiChat':
            kwargs['auto_continue'] = True

        messages = json_data['messages']
        if json_data.get('web_search'):
            if provider == "Bing":
                kwargs['web_search'] = True
            else:
                # ResourceWarning: unclosed event loop
                messages[-1]["content"] = get_search_message(messages[-1]["content"])

        model = json_data.get('model')
        model = model if model else models.default
        # patch = patch_provider if json_data.get('patch_provider') else None
        return {
            "model": model,
            "provider": provider,
            "messages": messages,
            "stream": True,
            "ignore_stream": True,
            # "patch_provider": patch,
            **kwargs
        }

    def _create_response_stream(self, kwargs) -> Generator[str, None, None]:
        """
        Creates and returns a streaming response for the conversation.

        Args:
            kwargs (dict): Arguments for creating the chat completion.

        Yields:
            str: JSON formatted response chunks for the stream.

        Raises:
            Exception: If an error occurs during the streaming process.
        """
        try:
            first = True
            for chunk in ChatCompletion.create(**kwargs):
                if first:
                    first = False
                    yield self._format_json('provider', get_last_provider(True))
                if isinstance(chunk, Exception):
                    logging.exception(chunk)
                    yield self._format_json('message', get_error_message(chunk))
                else:
                    yield self._format_json('content', str(chunk))
        except Exception as e:
            logging.exception(e)
            from g4f.cookies import get_cookies
            print(get_cookies(".bing.com"))
            yield self._format_json('error', get_error_message(e))

    def _format_json(self, response_type: str, content) -> str:
        """
        Formats and returns a JSON response.

        Args:
            response_type (str): The type of the response.
            content: The content to be included in the response.

        Returns:
            str: A JSON formatted string.
        """

        return json.dumps({
            'type': response_type,
            response_type: content  # if encode else content
        }) + "\n"


def get_error_message(exception: Exception) -> str:
    """
    Generates a formatted error message from an exception.

    Args:
        exception (Exception): The exception to format.

    Returns:
        str: A formatted error message string.
    """
    return f"{get_last_provider().__name__}: {type(exception).__name__}: {exception}"
