import re


def process_string(input_string):
    # Паттерн для поиска чисел с минимум двумя цифрами после точки
    pattern = r'\.(\d{2,})(?=\D|$)'

    result_string = re.sub(pattern, lambda x: '.' + x.group(1)[:2], input_string)

    return result_string


def file_writer(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        new_file_string = process_string(file.read())
    with open(file_name[:-4] + '_g.svg', "w", encoding="utf-8") as new_file:
        new_file.write(new_file_string)
    return new_file_string


if __name__ == '__main__':
    # Пример использования
    output_string = file_writer('''D:\Программирование\IDEA\coolinary\coolinary\static\svg\pin.svg''')
    # output_string = process_string("Это пример чисел: 3.1415, 2.7182, 123.45, -0.123, 42")
    print(output_string)
