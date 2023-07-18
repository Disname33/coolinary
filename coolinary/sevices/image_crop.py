import base64
import os
from io import BytesIO
from time import time_ns

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def decode64(base64_image):
    # base64_image = base64_image.replace('data:image/jpeg;base64,', '')
    # base64_image = base64_image.replace(' ', '+')  # Возможно не пригодится
    image_data = base64.b64decode(base64_image[21:])
    image_stream = BytesIO(image_data)
    image = Image.open(image_stream)
    image.thumbnail((440, 440), Image.LANCZOS)
    image_stream = BytesIO()
    image.save(image_stream, format='PNG', quality=90)
    return image_stream


def base64_to_bd(base64_image, profile):
    image_stream = decode64(base64_image)
    delete_previous_avatar(profile)
    filename = f"{profile.user.id}_{time_ns()}.png"
    processed_image = InMemoryUploadedFile(
        image_stream,
        None,
        filename,
        'image/jpeg',
        image_stream.tell(),
        None
    )
    profile.avatar = processed_image
    profile.avatar.name = filename


def delete_previous_avatar(profile):
    previous_path = 'media/' + profile.avatar.name
    if os.path.isfile(previous_path):
        os.remove(previous_path)
