import os
from io import BytesIO

from PIL import Image
from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Введите пароль ещё раз', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')
        return cd['password2']


def generate_filename(user_id, filename):
    ext = os.path.splitext(filename)[1]
    return f"{user_id}{ext}"


class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {'name': forms.FileInput(attrs={'class': "form-control btn btn-primal"})}

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['avatar']:
            user_id = instance.user_id
            avatar = self.cleaned_data['avatar']
            # filename = generate_filename(user_id, avatar.name)
            filename = f"{user_id}.jpg"
            previous_path = 'media/avatars/' + filename
            if os.path.isfile(previous_path):
                os.remove(previous_path)
            image = Image.open(avatar)
            image.thumbnail((440, 440), Image.LANCZOS)
            image_stream = BytesIO()
            image.save(image_stream, format='JPEG', quality=90)
            processed_image = InMemoryUploadedFile(
                image_stream,
                None,
                avatar.name,
                'image/jpeg',
                image_stream.tell(),
                None
            )
            instance.avatar = processed_image
            instance.avatar.name = filename
        if commit:
            instance.save()
        return instance
