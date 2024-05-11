import asyncio

import openai

from coolinary.secret.secret import openai_api_key

openai.api_key = openai_api_key
welcome_update_in_process = False


async def davinci(prompt):
    model_engine = "text-davinci-003"
    response = await openai.Completion.acreate(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


async def turbo_3_5(message):
    messages = messages_update([], "user", message)
    return await get_response(messages)


def messages_update(messages, role, content):
    messages.append({'role': role, 'content': content})
    return messages


async def get_response(messages):
    model_engine = "gpt-3.5-turbo"
    response = await openai.ChatCompletion.acreate(
        model=model_engine,
        messages=messages
    )
    return response.choices[0].message.content


# async def get_last_message_from_async_response(messages):
#     response = await get_response(messages)
#     return response['choices'][0]['message']['content']
#
#
# def get_last_message_from_response(messages):
#     response = asyncio.run(get_response(messages))
#     return response['choices'][0]['message']['content']

def get_welcome_message():
    try:
        file_path = "chatGPT/services/welcomeGPT.txt"
        with open(file_path, 'r', encoding="utf-8") as file:
            welcome = file.read()
            return welcome
    except FileNotFoundError as e:
        return ""


def get_welcome_message_and_update():
    import threading
    global welcome_update_in_process
    file_path = "chatGPT/services/welcomeGPT.txt"

    async def get_new_welcome_message():
        global welcome_update_in_process
        welcome_update_in_process = True
        temp = await turbo_3_5("Напиши приветственную речь пользователю чата от лица "
                               "искусственного интеллекта на 80 слов")
        with open(file_path, 'w', encoding="utf-8") as welcome_file:
            welcome_file.write(temp)
        welcome_update_in_process = False

    if not welcome_update_in_process:
        thread = threading.Thread(target=get_new_welcome_message)
        thread.start()

    return get_welcome_message()


def test():
    print(asyncio.run(
        davinci("Напиши приветственную речь пользователям от лица искусственного интеллекта на 100 слов")
    ))
    print("----------------------gpt-3.5-turbo-------------------------")
    print(asyncio.run(
        get_response("Напиши приветственную речь пользователю чата от лица искусственного "
                     "интеллекта на 80 слов")
    ))


def create_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url


def moderation(prompt):
    response = openai.Moderation.create(input=prompt)
    return response["results"][0]


if __name__ == '__main__':
    user_input = input()
    print(create_image(user_input))

    # current_messages = []
    # loop = asyncio.get_event_loop()
    # while True:
    #     user_input = input()
    #     messages_update(current_messages, "user", user_input)
    #     model_response = loop.run_until_complete(get_response(current_messages))
    #     print(model_response)
    #     messages_update(current_messages, "assistant", model_response)
