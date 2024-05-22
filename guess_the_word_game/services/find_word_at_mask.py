import re


def get_all_words_at_length(length=5):
    with open(f"word/{length}_letter_word.txt", "r", encoding="utf-8") as file:
        return [word[:length] for word in file.readlines()]


def replace_stars_with_russian_letters(pattern: str) -> str:
    escaped_pattern = re.escape(pattern)
    regex_pattern = escaped_pattern.replace(r'\*', '[а-я]')
    return regex_pattern



def find_matches_in_list(pattern: str, word_list: list) -> list:
    regex_pattern = replace_stars_with_russian_letters(pattern)
    compiled_regex = re.compile(regex_pattern)
    matches = [word for word in word_list if compiled_regex.fullmatch(word)]
    return matches


def find_matches_with_letters(pattern: str, word_list: list, letters="") -> list:
    regex_pattern = replace_stars_with_russian_letters(pattern)
    for letter in letters:
        regex_pattern = f"(?=.*{letter.lower()})" + regex_pattern
    compiled_regex = re.compile(regex_pattern)
    return [word for word in word_list if compiled_regex.fullmatch(word)]


def replace_non_russian_letters(pattern: str) -> str:
    regex_pattern = ''.join(
        '[а-я]' if not re.match(r'[а-я]', char) else char
        for char in pattern
    )
    return regex_pattern
    # escaped_pattern = re.escape(pattern)
    # regex_pattern = escaped_pattern.replace(r'[^а-я]', '[а-я]')
    # return regex_pattern


def find_matches_with_conditions(pattern: str, word_list, letters="", excluded_letters=""):
    regex_pattern = replace_non_russian_letters(pattern)
    for letter in letters.lower():
        regex_pattern = f"(?=.*{letter})" + regex_pattern
    for excluded_letter in excluded_letters.lower():
        regex_pattern = f"(?!.*{excluded_letter})" + regex_pattern
    compiled_regex = re.compile(regex_pattern)
    return [word for word in word_list if compiled_regex.fullmatch(word)]


if __name__ == '__main__':
    pattern = "*дм**"
    letters = ['и']
    print(pattern)
    words = get_all_words_at_length(len(pattern))
    # matches = find_matches_in_list(pattern.lower(), words)
    matches = find_matches_with_letters(pattern.lower(), words, letters)
    print(matches if len(matches) else 'Не смогли подобрать слова!')
