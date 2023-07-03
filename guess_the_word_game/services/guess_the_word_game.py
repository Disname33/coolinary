import json
import random
from re import match
from typing import NamedTuple

from .timer import elapsed_time, start_timer
from ..config import *
from ..models import CurrentSession


class NounWithDefinition(NamedTuple):
    # Определение именованного кортежа с именами полей
    noun: str
    definition: str

    def __str__(self):
        return self.noun.capitalize() + " — " + self.definition + ' '


def get_attempts(difficulty: int):
    if 4 <= difficulty <= 7:
        return attempts[difficulty]
    if difficulty < 6:
        return 6
    return difficulty * 2 - 4


def remaining_attempts(current_session: CurrentSession) -> int:
    return get_attempts(current_session.difficulty) - len(current_session.entered_words_list)


def get_meaning_word(word: str) -> str:
    with open(russian_nouns_with_definition_json, "r", encoding="utf-8") as file:
        # Загружаем данные из файла
        meaning = json.load(file)
    return meaning[word]["definition"]


def _find_next_word(word: str, string: str) -> str | None:
    words = string.split()
    if word in words:
        index = words.index(word)
        if index < len(words) - 1:
            return words[index + 1].rstrip('.')
    return None


def remove_line_with_word(word: str) -> str:
    word = word.lower().strip()
    file_path = f"word/{len(word)}_letter_word.txt"
    # Открываем файл на чтение и запись
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()  # Читаем все строки из файла

    # Находим и удаляем строки, содержащие указанное слово
    new_lines = [line for line in lines if word not in line]

    # Открываем файл на запись и записываем новые строки
    with open(file_path, 'w', encoding="utf-8") as file:
        file.writelines(new_lines)

    if len(lines) > len(new_lines):
        with open(file_path + "_deleted", 'a', encoding="utf-8") as file:
            file.writelines(word + "\n")
        return f"слово {word} удалено"
    else:
        return f"слово {word} не найдено"


def get_full_meaning_word(word: str) -> str:
    meaning_word = get_meaning_word(word)
    try:
        next_word = None
        if " см. " in meaning_word:
            next_word = _find_next_word("см.", meaning_word)
        elif " То же, что: " in meaning_word:
            next_word = _find_next_word("что:", meaning_word)
        if next_word is not None and next_word != 'также' and next_word != '':
            return meaning_word + " " + str(NounWithDefinition(noun=next_word, definition=get_meaning_word(next_word)))
    except Exception as e:
        print(e)
    return meaning_word


def is_there_a_word_meaning(word: str) -> bool:
    with open(russian_nouns_with_definition_json, "r", encoding="utf-8") as file:
        meaning = json.load(file)
    return word in meaning


def get_random_line(lines) -> str:
    # Генерируем случайный индекс строки из списка
    random_index = random.randrange(len(lines)) - 1
    # Получаем случайную строку из списка по сгенерированному индексу и удаляем символ новой строки
    return lines[random_index].strip()


def open_file(difficulty: int):
    with open(f"word/{difficulty}_letter_word.txt", "r", encoding="utf-8") as file:
        # Читаем все строки из файла возвращаем их в список
        return file.readlines()


def get_random_noun(difficulty: int) -> str:
    lines = open_file(difficulty)
    return get_random_line(lines)


def get_random_noun_with_mean(difficulty: int) -> NounWithDefinition:
    random_word = get_random_noun(difficulty)
    return NounWithDefinition(noun=random_word, definition=get_full_meaning_word(random_word))


def correct_length(text: str, difficulty) -> bool:
    return len(text) == difficulty


def is_russian(text: str) -> bool:
    return match(r'^[а-я]+$', text) is not None


def is_meaning(text: str) -> bool:
    with open(russian_nouns_with_definition_json, "r", encoding="utf-8") as file:
        # Загружаем данные из файла
        meaning = json.load(file)
    return text in meaning


# Список пустой или не содержит введённое слово?
def is_already_entered(text: str, _entered_words_list: []) -> bool:
    return _entered_words_list and text in _entered_words_list


def input_validation(text: str, current_session: CurrentSession) -> bool:
    if not correct_length(text, current_session.difficulty):
        current_session.notice = notice_wrong_len.format(current_session.difficulty)
    elif not is_russian(text):
        current_session.notice = notice_not_Cyrillic
    elif not is_meaning(text):
        current_session.notice = notice_not_means_word
    elif is_already_entered(text, current_session.entered_words_list):
        current_session.notice = notice_already_entered.format(text)
    else:
        return True
    return False


def find_matching_letters(entered_word: str, current_session: CurrentSession) -> str:
    # R - нет; B - есть буква, но на другой позиции; G - полное совпадение
    coincidences = ""
    for i in range(current_session.difficulty):
        if current_session.hidden_word[i] == entered_word[i]:
            coincidences += 'G'
        elif entered_word[i] in current_session.hidden_word:
            coincidences += 'B'
        else:
            coincidences += 'R'
    return coincidences


def word_coloring(entered_word: str, coincidences: str) -> str:
    color_word = ""
    for entered_letter, coincidence in zip(entered_word.upper(), coincidences):
        color_word = color_word + colors[coincidence].format(entered_letter)
    return color_word


def word_list_coloring(entered_words_list: [str], coincidences_list: [str]) -> [str]:
    colored__words_list = []
    for entered_word, coincidences in zip(entered_words_list, coincidences_list):
        colored__words_list.append(word_coloring(entered_word, coincidences))
    return colored__words_list


def is_win(entered_word: str, current_session: CurrentSession) -> bool:
    return current_session.hidden_word == entered_word


def is_loss(current_session: CurrentSession):
    return len(current_session.entered_words_list) >= get_attempts(current_session.difficulty)


def notice_loss(current_session: CurrentSession) -> str:
    return notice_final.format(current_session.hidden_word.upper(), get_full_meaning_word(current_session.hidden_word))


def notice_congratulations_final(current_session: CurrentSession) -> str:
    return (
            notice_congratulations + notice_final).format(
        len(current_session.entered_words_list),
        int(elapsed_time(current_session.start_time)),
        current_session.hidden_word.upper(),
        get_full_meaning_word(current_session.hidden_word)
    )


def input_cycle(entered_string: str, current_session: CurrentSession):
    current_session.notice = ""
    current_session.entered_words_list.append(entered_string)
    coincidences = find_matching_letters(entered_string, current_session)
    current_session.coincidences_list.append(coincidences)
    current_session.save()


def start_new_game(current_session):
    current_session.notice = ""
    current_session.entered_words_list = []
    current_session.coincidences_list = []
    current_session.start_time = start_timer()
    current_session.hidden_word = get_random_noun(current_session.difficulty)


def get_current_session(user) -> CurrentSession:
    current_session = None
    try:
        current_session = CurrentSession.objects.get(user=user)
    except Exception as e:
        print(e)
    if not current_session:
        current_session = CurrentSession.create(user=user)
    if current_session.hidden_word == 'старт':
        current_session.hidden_word = get_random_noun(current_session.difficulty)
    return current_session


if __name__ == '__main__':
    for _ in range(100):
        print(get_random_noun_with_mean(5))
