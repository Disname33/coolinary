import random

from g4f import ChatCompletion
from g4f.client import Client

from coolinary.secret.secret import BING_U_LIST, GOOGLE_Secure_1PSID


def get_response(messages, model_engine="gpt-4"):
    client = Client()
    response = client.chat.completions.create(
        model=model_engine,
        messages=messages
    )
    return response.choices[0].message.content


def set_all_cookies():
    from g4f.cookies import set_cookies
    BING_U = random.choice(BING_U_LIST)
    # print(BING_U)
    set_cookies(".bing.com", {"_U": BING_U})
    # set_cookies("chat.openai.com", {"access_token": openai_api_key})
    set_cookies(".google.com", {"__Secure-1PSID": GOOGLE_Secure_1PSID})


def create_image(prompt: str):
    client = Client()
    set_all_cookies()
    # response = client.images.generate(
    #     model="gpt-4o",
    #     prompt=prompt,
    # )
    kwargs = {}
    image_url = ChatCompletion.create(**{
        "model": "gpt-4o",
        "provider": 'BingCreateImages',
        "messages": [{'role': 'user', 'content': prompt}],
        "stream": False,
        "ignore_stream": True,
        "return_conversation": True,
        **kwargs,
    })
    print(image_url)
    # image_url = response.data[0].url
    return image_url


def start_gui():
    from g4f.gui import run_gui
    set_all_cookies()
    run_gui()


if __name__ == '__main__':
    # from g4f.cookies import set_cookies, load_cookies_from_browsers
    # bing = load_cookies_from_browsers("bing.com")
    # set_cookies(".bing.com", bing)
    # print(bing)
    # you = load_cookies_from_browsers("you.com")
    # set_cookies(".you.com", you)
    # print(you)
    start_gui()
