import base64

import matplotlib.dates as m_dates
import matplotlib.pyplot as plt
from six import BytesIO


def plot_chart(x, y, x_label='X-координаты', y_label='Y-координаты',
               title='Название графика', color='red', plot_type='plot') -> base64:
    plt.figure(figsize=(6, 5))
    if plot_type == "bar":
        plt.bar(x, y, color=color)
    else:
        plt.plot(x, y, color=color)
    plt.xlabel(x_label)
    plt.ylabel(y_label).set_position((1, 0.8))
    plt.title(title)
    # Настройка меток оси X
    ax = plt.gca()
    ax.xaxis.set_major_locator(m_dates.DayLocator())
    ax.xaxis.set_major_formatter(m_dates.DateFormatter("%m.%d"))
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.2)
    plt.grid(True)

    # Создание объекта-потока для сохранения изображения графика
    image_stream = BytesIO()

    # Сохранение изображения графика в поток
    plt.savefig(image_stream, format='png')
    plt.close()

    # Перемещение указателя потока в начало
    image_stream.seek(0)

    # Преобразование изображения в строку в формате base64
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    return image_base64
