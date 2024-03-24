import random

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


def create_image(prompt):
    client = Client()
    set_all_cookies()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
    )
    image_url = response.data[0].url
    return image_url


def start_gui():
    from g4f.gui import run_gui

    set_all_cookies()
    run_gui()


if __name__ == '__main__':
    start_gui()
