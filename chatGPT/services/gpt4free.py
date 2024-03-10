from g4f.client import Client

from coolinary.secret.secret import BING_U, GOOGLE_Secure_1PSID


def get_response(messages, model_engine="gpt-4"):
    client = Client()
    response = client.chat.completions.create(
        model=model_engine,
        messages=messages
    )
    return response.choices[0].message.content


def set_all_cookies():
    from g4f.cookies import set_cookies

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

# stream = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": "Самые красивые породы кошек"}],
#     stream=True,
#
# )
# for chunk in stream:
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content or "", end="")


if __name__ == '__main__':
    from g4f.gui import run_gui

    set_all_cookies()
    run_gui()
