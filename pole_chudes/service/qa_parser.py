import json

import requests
from bs4 import BeautifulSoup

from ..models import Riddle


def add_riddles_from_json(json_file_path="word/qa_data.json"):
    # Чтение данных из JSON файла
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    for item in data['RECORDS']:
        word = item['answer']
        question = item['question']
        if not Riddle.objects.filter(word=word).exists():
            Riddle.objects.create(word=word, question=question)


def save_riddles_from_html_to_json(html_file_path="qa.html", json_file_path="word/qa_data.json"):
    with open(html_file_path, 'r', encoding="utf-8") as html_file:
        html_content = html_file
    soup = BeautifulSoup(html_content, 'html.parser')
    question_items = soup.find_all(class_='quest_item')
    qa_list = []
    for item in question_items:
        question_element = item.find(class_='quest_question')
        answer_element = item.find(class_='quest_answer')
        question_text = question_element.get_text(strip=True)
        answer_text = answer_element.get('data-answer')

        if len(answer_text) < 6:
            continue
        qa_dict = {'question': question_text, 'answer': answer_text}
        qa_list.append(qa_dict)

    # Конвертируем список в JSON и сохраняем в файл
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(qa_list, json_file, ensure_ascii=False, indent=4)


def parse_and_add_riddles(url='https://polechudes-otvet.ru/'):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')[2:]
        for row in rows:
            # Ищем ссылку внутри элемента td
            link = row.find('td').find('a')
            if link:
                riddle_response = requests.get(link.get('href'))
                if riddle_response.status_code == 200:
                    riddle_soup = BeautifulSoup(riddle_response.text, 'html.parser')
                    question_element = riddle_soup.find('h1', class_='text-center')
                    answer_element = riddle_soup.find('strong')

                    if question_element and answer_element:
                        question = question_element.text.strip()
                        answer = answer_element.text[6:].split('/')[0].strip().capitalize()

                        if len(answer) > 5 and not Riddle.objects.filter(word=answer).exists():
                            Riddle.objects.create(word=answer, question=question)
                            print(f"Добавлен новый вопрос: {question}, ответ: {answer}")
                        else:
                            print(f"Слово {answer} уже существует в базе данных.")
                else:
                    print(f"Не удалось получить данные по ссылке: {link.get('href')}")
    else:
        print("Ошибка при выполнении запроса к странице.")
