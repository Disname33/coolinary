from django import forms
from django.utils import timezone

from coolinary.forms import BootstrapButtonRadioSelect
from .models import Debt


class DebtForm(forms.ModelForm):
    NEW_CREDIT = 'new_credit'
    NEW_CONTRIBUTION = 'new_contribution'

    TRANSACTION_CHOICES = [
        (NEW_CREDIT, 'Новый кредит'),
        (NEW_CONTRIBUTION, 'Новый взнос'),
    ]

    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_CHOICES,
        widget=BootstrapButtonRadioSelect(attrs={'label_class': 'col-6'}),
        label='Тип транзакции',
        initial=NEW_CONTRIBUTION
    )

    class Meta:
        model = Debt
        fields = ['user', 'interest_rate', 'principal_amount', 'paid_amount', 'payment_date']

        widgets = {
            'principal_amount': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': 'any',
            }),
            'interest_rate': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': 'any',
            }),
            'paid_amount': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': 'any',
            }),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'min': "1992-01-11",
                'type': "date"
            }),
        }

    def __init__(self, *args, **kwargs):
        super(DebtForm, self).__init__(*args, **kwargs)
        last_debt = Debt.objects.order_by("id").last()
        rate = last_debt.interest_rate if last_debt else 12
        user = last_debt.user if last_debt else 1
        self.fields['interest_rate'].initial = rate
        self.fields['user'].initial = user
        self.fields['principal_amount'].initial = 0
        self.fields['paid_amount'].initial = 0
        self.fields['payment_date'].initial = timezone.now().strftime("%Y-%m-%d")

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        paid_amount = cleaned_data.get('paid_amount')
        payment_date = cleaned_data.get('payment_date')
        if payment_date is None:
            self.add_error('payment_date', forms.ValidationError('Введите дату.'))
        if transaction_type == self.NEW_CONTRIBUTION:
            cleaned_data['principal_amount'] = 0
            if paid_amount != 0:
                last_debt = Debt.objects.filter(user=cleaned_data['user']).order_by("payment_date").last()
                if last_debt:
                    cleaned_data['interest_rate'] = last_debt.interest_rate
                    cleaned_data['principal_amount'] = last_debt.current_debt(formatted_date=payment_date)
        else:
            cleaned_data['paid_amount'] = 0

        return cleaned_data

    def as_row(self):
        """Return this form rendered as HTML <div class='row'>s."""
        return self._html_output(
            normal_row='<div class="row my-1 %(html_class_attr)s"><div class="left-part"> %(label)s </div><div '
                       'class="right-part"> %(field)s%(help_text)s</div></div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )
