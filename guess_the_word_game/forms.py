from django import forms


class GameForms(forms.Form):
    enter_word = forms.CharField(max_length=10,
                                 widget=forms.TextInput(
                                     attrs={
                                         'type': 'text',
                                         'placeholder': "Введите слово",
                                         'aria-label': "Recipient's username",
                                         'aria-describedby': "button-addon2",
                                         'class': "form-control"
                                     })
                                 )

# class GameForms(Form):
#
#     class Meta:
#         fields = ["enter_word"]
#         widgets = {
#             "enter_word": TextInput(attrs={
#                 'type': 'text',
#                 'placeholder': "Введите слово",
#                 'aria-label': "Recipient's username",
#                 'aria-describedby': "button-addon2",
#                 'class': "form-control"
#             })
#         }
