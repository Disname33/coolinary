import json
import re
from datetime import datetime

from django.http import JsonResponse, StreamingHttpResponse
from g4f import ChatCompletion
# from g4f.gui.server.config import special_instructions
from requests import get

from .config import special_instructions


class Backend_Api:
    def __init__(self, config: dict) -> None:
        """
        Initialize the Backend_Api class.
        :param config: Configuration dictionary
        """
        self.routes = {
            '': self.conversation,
        }

    @staticmethod
    def generate_stream(response, jailbreak):
        """
        Generate the conversation stream.

        :param response: Response object from ChatCompletion.create
        :param jailbreak: Jailbreak instruction string
        :return: Generator object yielding messages in the conversation
        """
        if getJailbreak(jailbreak):
            response_jailbreak = ''
            jailbroken_checked = False
            for message in response:
                response_jailbreak += message
                if jailbroken_checked:
                    yield message.encode('utf-8')  # Yield encoded message directly
                else:
                    if response_jailbroken_success(response_jailbreak):
                        jailbroken_checked = True
                    if response_jailbroken_failed(response_jailbreak):
                        yield response_jailbreak.encode('utf-8')  # Yield encoded message directly
                        jailbroken_checked = True
        else:
            for message in response:
                yield message.encode('utf-8')  # Yield encoded message directly

    @staticmethod
    def conversation(request):
        """
        Handles the conversation route.

        :param request: Django HTTP request
        :return: JsonResponse or StreamingHttpResponse containing the generated conversation stream
        """
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

        try:
            json_string = request.body.decode('utf-8')
            data = json.loads(json_string)
            conversation_id = data['conversation_id']
            jailbreak = data['jailbreak']
            model = data['model']
            messages = build_messages(data)

            response = ChatCompletion.create(
                model=model,
                chatId=conversation_id,
                messages=messages,
            )

            return StreamingHttpResponse(generate_stream(response, jailbreak), content_type='text/event-stream')

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)

            return JsonResponse({
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"
            }, status=400)


def build_messages(data):
    """
    Build the messages for the conversation.

    :param data: Dictionary containing request data
    :return: List of messages for the conversation
    """
    _conversation = data['meta']['content']['conversation']
    internet_access = data['meta']['content']['internet_access']
    prompt = data['meta']['content']['parts'][0]

    # Add the existing conversation
    conversation = _conversation

    # Add web results if enabled
    if internet_access:
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = f'Current date: {current_date}. ' + prompt["content"]
        search_results = fetch_search_results(query)
        conversation.extend(search_results)

    # Add jailbreak instructions if enabled
    if jailbreak_instructions := getJailbreak(data.get('jailbreak', None)):
        conversation.extend(jailbreak_instructions)

    # Add the prompt
    conversation.append(prompt)

    # Reduce conversation size to avoid API Token quantity error
    if len(conversation) > 3:
        conversation = conversation[-4:]

    return conversation


def fetch_search_results(query):
    """
    Fetch search results for a given query.

    :param query: Search query string
    :return: List of search results
    """
    search = get('https://ddg-api.herokuapp.com/search',
                 params={
                     'query': query,
                     'limit': 3,
                 })

    snippets = ""
    for index, result in enumerate(search.json()):
        snippet = f'[{index + 1}] "{result["snippet"]}" URL:{result["link"]}.'
        snippets += snippet

    response = "Here are some updated web searches. Use this to improve user response:"
    response += snippets

    return [{'role': 'system', 'content': response}]


def generate_stream(response, jailbreak):
    """
    Generate the conversation stream.

    :param response: Response object from ChatCompletion.create
    :param jailbreak: Jailbreak instruction string
    :return: Generator object yielding messages in the conversation
    """
    if getJailbreak(jailbreak):
        response_jailbreak = ''
        jailbroken_checked = False
        for message in response:
            response_jailbreak += message
            if jailbroken_checked:
                yield message
            else:
                if response_jailbroken_success(response_jailbreak):
                    jailbroken_checked = True
                if response_jailbroken_failed(response_jailbreak):
                    yield response_jailbreak
                    jailbroken_checked = True
    else:
        yield from response


def response_jailbroken_success(response: str) -> bool:
    """
    Check if the response has been jailbroken.

    :param response: Response string
    :return: Boolean indicating if the response has been jailbroken
    """
    act_match = re.search(r'ACT:', response, flags=re.DOTALL)
    return bool(act_match)


def response_jailbroken_failed(response):
    """
    Check if the response has not been jailbroken.

    :param response: Response string
    :return: Boolean indicating if the response has not been jailbroken
    """
    return False if len(response) < 4 else not (response.startswith("GPT:") or response.startswith("ACT:"))


def getJailbreak(jailbreak):
    """
    Check if jailbreak instructions are provided.

    :param jailbreak: Jailbreak instruction string
    :return: Jailbreak instructions if provided, otherwise None
    """
    if jailbreak != "default":
        special_instructions[jailbreak][0]['content'] += special_instructions['two_responses_instruction']
        if jailbreak in special_instructions:
            special_instructions[jailbreak]
            return special_instructions[jailbreak]
        else:
            return None
    else:
        return None
