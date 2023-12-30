from datetime import datetime

from django.db import models
from django.utils import timezone as tz


class Debt(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма кредита')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ставка')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Сумма взноса')
    payment_date = models.DateField(null=True, blank=True, verbose_name='Дата')

    def remaining_amount(self):
        return self.principal_amount - self.paid_amount

    def current_debt(self, date=None):
        if date is None:
            formatted_date = tz.now().date()
        else:
            formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
        return self.principal_amount * (1 + ((formatted_date - self.payment_date).days * self.interest_rate / 36000))
