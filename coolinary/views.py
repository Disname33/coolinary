from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import UserRegistrationForm, AvatarUploadForm
from .models import UserProfile


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
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Создание объекта UserProfile, если он не существует
        user_profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)  # Не сохраняем форму пока
            form.instance.user = request.user  # Присваиваем пользователю
            form.save()  # Теперь сохраняем форму вместе с пользователем
    else:
        initial_data = {
            'avatar': user_profile.avatar,
        }
        form = AvatarUploadForm(initial=initial_data)
    return render(request, 'registration/profile.html', {'form': form, "profile": user_profile})
