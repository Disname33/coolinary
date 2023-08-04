import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render

from .forms import UserRegistrationForm, UserProfileForm, EmailChangeForm
from .models import UserProfile
from .services.image_crop import base64_to_bd, delete_previous_avatar


def index(request):
    return render(request, 'home/index.html')


def device_info(request):
    return render(request, 'home/device_info.html')


def work_trip(request):
    return render(request, 'work_trip/work_trip.html')


def register(request):
    if request.user.is_authenticated:
        return render(request, 'home/index.html')

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
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
