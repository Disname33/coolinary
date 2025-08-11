import json

from brake.decorators import ratelimit
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import requires_csrf_token

from .forms import UserRegistrationForm, UserProfileForm, EmailChangeForm
from .models import UserProfile
from .services.image_crop import base64_to_bd, delete_previous_avatar


def index(request):
    return render(request, 'home/index.html')


def device_info(request):
    return render(request, 'home/device_info.html')


def handler404(request, exception=""):
    return render(request, 'registration/error404.html', {'exception': exception}, status=404)


@requires_csrf_token
def csrf_failure(request, reason=""):
    from django.contrib.sessions.models import Session
    error_text = 'Ключ доступа не верен или не прошёл проверку'
    if not "csrfmiddlewaretoken" in request.POST:
        error_text = "Отсутствует ключ доступа"
    elif not request.POST.get("csrfmiddlewaretoken"):
        error_text = "Ключ доступа пуст"
    if request.session.is_empty():
        error_text = "Пустая сессия, возможно она истекла"
    elif not request.session.exists(request.session.session_key):
        error_text = "Устаревшая сессия, уже используется новый ключ доступа"
    else:
        try:
            session = Session.objects.get(session_key=request.session.session_key)
            if session.expire_date < timezone.now():
                error_text = "Сессия просрочена"
        except Session.DoesNotExist:
            error_text = "Сессия не найдена"
    return render(request, 'registration/error403.html', {'error_text': error_text, 'reason': reason}, status=403)


@ratelimit(rate='2/15m', method='POST', block=True)
def secure_login_view(request):
    from django.contrib.auth.views import LoginView
    return LoginView.as_view()(request)


@ratelimit(rate='2/15m', method='POST', block=True)
def register(request):
    if request.user.is_authenticated:
        return render(request, 'home/index.html')

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'user_form': user_form})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if request.POST.get('save'):
            status = {"status": "OK"}
            if request.POST.get('new_password1'):
                password_change_form = PasswordChangeForm(request.user, request.POST)
                if password_change_form.is_valid():
                    user = password_change_form.save()
                    # обновляем сессию пользователя, чтобы избежать выхода из системы
                    update_session_auth_hash(request, user)
                    status["password"] = 'Пароль успешно изменен!'
                else:
                    status = {"status": 'error', "error": 'Неверный пароль!'}
            if request.POST.get('email') or request.POST.get('old_email'):
                email_change_form = EmailChangeForm(request.POST, instance=request.user)
                if email_change_form.is_valid():
                    email_change_form.save()
                    status["email"] = 'Email успешно изменен!'
                else:
                    status = {"status": 'error', "error": 'Неверный Email!'}
            if request.POST.get('first_name') or request.POST.get('last_name'):
                request.user.first_name = request.POST.get('first_name')
                request.user.last_name = request.POST.get('last_name')
                request.user.save()
            form = UserProfileForm(request.POST, instance=user_profile)
            print(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponse(json.dumps(status), content_type='application/json')
        else:
            content = {"avatar": "/static/default_avatar.png"}
            if request.POST.get('delete_avatar'):
                delete_previous_avatar(user_profile)
                user_profile.avatar.delete()
            if image64 := request.POST.get('file'):
                base64_to_bd(image64, user_profile)
                content = {"avatar": user_profile.avatar.url}
            user_profile.save()
            return HttpResponse(json.dumps(content), content_type='application/json')
    form = UserProfileForm(instance=user_profile)
    return render(request, 'registration/profile.html', {'form': form})
