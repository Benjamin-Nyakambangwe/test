from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm


@csrf_protect
def user_login(request):
    '''Log the user into the system'''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('graded-organizations')
        else:
            messages.error(request, 'Invalid Login Credentials')

    return render(request, 'accounts/login.html')


def register(request):
    form = CreateUserForm(request.POST or None)

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')
