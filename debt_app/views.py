from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from .models import Debt


@login_required
def debt_info(request):
    user_debts = Debt.objects.filter(user=request.user).order_by("payment_date")
    current_debt = 0
    if user_debts:
        current_debt = user_debts.last().current_debt()
    return render(request, 'debt_app/debt_info.html',
                  {'user_debts': user_debts, 'current_debt': current_debt})


@login_required
def debt_admin(request):
    if request.user.id == 1:
        if select_user := request.POST.get('select_user'):
            new_amount = Decimal(request.POST.get('new_amount'))
            paid_amount = Decimal(request.POST.get('paid_amount'))
            rate = Decimal(request.POST.get('rate'))
            if new_amount != 0:
                date = request.POST.get('new_amount_date')
                debts = Debt.objects.create(user=User(select_user), principal_amount=new_amount, interest_rate=rate,
                                            paid_amount=0, payment_date=date)
                debts.save()
            elif paid_amount != 0:
                date = request.POST.get('paid_amount_date')
                last_debts = Debt.objects.filter(user=select_user).order_by("payment_date").last()
                principal_amount = last_debts.current_debt(date)
                if principal_amount - paid_amount < 1:
                    paid_amount = principal_amount
                debts = Debt.objects.create(user=User(select_user), principal_amount=principal_amount,
                                            interest_rate=last_debts.interest_rate, paid_amount=paid_amount,
                                            payment_date=date)
                debts.save()

            user_debts = Debt.objects.filter(user=select_user).order_by("payment_date")
            current_debt = 0
            if user_debts:
                current_debt = user_debts.last().current_debt()
            return render(request, 'debt_app/debt_info.html',
                          {'user_debts': user_debts, 'current_debt': current_debt})
        else:
            all_users = User.objects.all()
            return render(request, 'debt_app/debt_admin.html', {'all_users': all_users})
    else:
        return debt_info(request)
