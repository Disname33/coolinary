import os
from datetime import date
from io import BytesIO

from PIL import Image
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Введите пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Введите пароль ещё раз',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

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


class BootstrapButtonRadioSelect(forms.RadioSelect):
    template_name = 'modules/bootstrap-button-radio-select.html'


class DateInputNotLocale(forms.DateInput):
    def format_value(self, value):
        if value is None:
            return ""
        else:
            return value.strftime("%Y-%m-%d")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthday', 'country', 'city', 'display_option', 'gender']
        widgets = {
            'birthday': DateInputNotLocale(attrs={
                'class': 'form-control',
                'min': "1900-01-01",
                'max': date.today().strftime("%Y-%m-%d"),
                'type': "date"
            }),
            'gender': BootstrapButtonRadioSelect(attrs={'label_class': 'col-6'}),
            'display_option': BootstrapButtonRadioSelect(attrs={'label_class': 'col-6'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
        }

    def as_row(self):
        """Return this form rendered as HTML <div class='row'>s."""
        return self._html_output(
            normal_row='<div class="row %(html_class_attr)s"><div class="left-part"> %(label)s </div><div '
                       'class="right-part"> %(field)s%(help_text)s</div></div><hr>',
            error_row='%s',
            row_ender='</div>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )


class UserChangePasswordForm(PasswordChangeForm):
    class Meta:
        widgets = {
            'new_password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'old_password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def as_row(self):
        """Return this form rendered as HTML <div class='row'>s."""
        return self._html_output(
            normal_row='<div class="row %(html_class_attr)s"><div class="left-part"> %(label)s </div><div '
                       'class="right-part"> %(field)s%(help_text)s</div></div><hr>',
            error_row='%s',
            row_ender='</div>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )


class EmailChangeForm(forms.ModelForm):
    old_email = forms.EmailField(label='Старый Email',
                                 widget=forms.EmailInput(attrs={'class': 'form-control'}),
                                 required=False)

    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': 'Новый Email'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_old_email(self):
        old_email = self.cleaned_data.get("old_email")
        if old_email != self.instance.email:
            raise ValidationError(
                "Неверный Email. Введите текущий email пользователя.",
                code="email_mismatch",
            )
        return old_email
