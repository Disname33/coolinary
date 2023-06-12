from django.shortcuts import render
from .forms import UserRegistrationForm


def index(request):
    return render(request, 'home/index.html')


def device_info(request):
    return render(request, 'home/device_info.html')


def work_trip(request):
    return render(request, 'work_trip/work_trip.html')


def register(request):
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
