from django.forms import ModelForm, TextInput

from .models import City


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {'name': TextInput(attrs={
            'type': "text",
            'id': "city",
            'name': "name",
            'placeholder': "Введите город",
            'aria-label': "Recipient's username",
            'aria-describedby': "button-addon2",
            'class': "form-control"
        })
        }
