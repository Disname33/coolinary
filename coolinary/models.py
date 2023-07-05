# from django.contrib.auth.models import User
# from django.db import models
# import os
#
#
# def get_avatar_filename(instance, filename):
#     username = instance.user.username
#     ext = os.path.splitext(filename)[1]
#     return f'static/avatars/{username}{ext}'
#
#
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(upload_to=get_avatar_filename, default="static/avatar.png")
#
#     def __str__(self):
#         return self.user.username
