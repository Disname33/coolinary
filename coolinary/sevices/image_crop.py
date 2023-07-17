import base64
import os
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from coolinary.models import UserProfile


def decode64(base64_image):
    base64_image = base64_image.replace('data:image/jpeg;base64,', '')
    base64_image = base64_image.replace(' ', '+')
    # Декодирование base64 строки в бинарные данные
    image_data = base64.b64decode(base64_image)
    # Создание объекта BytesIO для работы с бинарными данными как с файлом
    image_stream = BytesIO(image_data)
    # Открытие изображения с помощью PIL
    image = Image.open(image_stream)
    image.thumbnail((440, 440), Image.LANCZOS)
    image_stream = BytesIO()
    image.save(image_stream, format='JPEG', quality=90)
    return image_stream

    # Указываете путь и имя файла, в который будет сохранено изображение
    # save_path = "output.jpg"  # замените "output.jpg" на свой путь и имя файла

    # Сохранение изображения
    # image.save(save_path)
    # Вы можете выполнять операции с изображением, например, отобразить его
    # image.show()


def base64_to_bd(base64_image, user):
    image_stream = decode64(base64_image)
    user_id = user.id
    filename = f"{user_id}.jpg"
    previous_path = 'media/avatars/' + filename
    if os.path.isfile(previous_path):
        os.remove(previous_path)
    processed_image = InMemoryUploadedFile(
        image_stream,
        None,
        filename,
        'image/jpeg',
        image_stream.tell(),
        None
    )
    profile = UserProfile.objects.get(user=user)
    profile.avatar = processed_image
    profile.avatar.name = filename
    profile.save()
