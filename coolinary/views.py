import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .forms import UserRegistrationForm
from .models import UserProfile
from .sevices.image_crop import base64_to_bd, delete_previous_avatar


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
        content = {"avatar": "/static/default_avatar.png"}
        if request.POST.get('delete_avatar'):
            delete_previous_avatar(user_profile)
            user_profile.avatar.delete()
        if image64 := request.POST.get('file'):
            base64_to_bd(image64, user_profile)
            content = {"avatar": user_profile.avatar.url}
        user_profile.save()
        return HttpResponse(json.dumps(content), content_type='application/json')
    return render(request, 'registration/profile.html')
