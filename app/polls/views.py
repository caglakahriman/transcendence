from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import User
from rest_framework import viewsets
from .forms import RegistrationForm
from .serializers import UserSerializer
from django.contrib.auth import authenticate


import json
import requests

class UserView(viewsets.ModelViewSet): #implementation for CRUD operations by default.
    serializer_class = UserSerializer
    queryset = User.objects.all()

def main(request):
    user_count = User.objects.all().count()
    context = {
        'user_count': user_count,
    }
    return render(request, "index.html", context=context)

def users(request):
    users = User.objects.all()
    context = {
        'users': [user.login for user in users],
    }
    return render(request, "users.html", context=context)


def auth42(request):
    code = request.GET.get('code')
    body = {
    'grant_type': 'authorization_code',
    'client_id': 'u-s4t2ud-b4b7ae8076ad4f54587fc9c6a82d2683386f891c8a757445c10a4bfd57c3a636',
    'client_secret': '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',
    'code': f'{code}',
    'redirect_uri': 'http://localhost:8000/auth42'
    }
    r = requests.post('https://api.intra.42.fr/oauth/token', data=body)

    user = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + r.json()['access_token']})

    user_info = json.dumps(user.json(), indent=4)
    if (User.objects.filter(login=user.json()['login']).exists() == False):
        new_user = User.objects.create(login=user.json()['login'], token=r.json()['refresh_token'])
        new_user.save()
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            token = form.cleaned_data['token']
            if (User.objects.filter(login=login).exists()):
                user = User.objects.get(login=login)
                if (user.token == token):
                    messages.success(request, f'You are logged in as {login}')
                    #authenticate(request, username=login, password=token)
                    return redirect("main")
                else:
                    messages.error(request, f'Invalid password')
                    return redirect("login")
            else:
                messages.error(request, f'Are you sure you are registered?')
                return redirect('login')
    else:
        form = RegistrationForm()
        return render(request, "login.html", {'form': RegistrationForm()})

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            token = form.cleaned_data['token']
            if (User.objects.filter(login=login).exists()):
                messages.error(request, f"This username is already taken: {login}. C'mon, be more creative!")
                return redirect("register")
            elif (token != ""):
                new_user = User.objects.create(login=login, token=token)
                new_user.save()
                messages.success(request, f"You've successfully registered as {login}!")
                return redirect("main")
    else:
        form = RegistrationForm()
        return render(request, "register.html", {'form': form})

def pollindex(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def searchUser(request, user_name):
    users = User.objects.all()
    user_names = [user.login for user in users]

    if (user_name in user_names):
        return HttpResponse("User you are looking for exists: %s." % user_name)
    else:
        return HttpResponse("THIS USER DOES NOT EXIST")