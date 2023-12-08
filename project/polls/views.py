from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from rest_framework import viewsets
from .forms import RegistrationForm, UsernameForm, AvatarForm
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from django.http import JsonResponse
#from .serializers import UserSerializer
from .models import Profile
#from .signals import update_profile_signal

import os
import environ
import json
import requests


'''
class UserView(viewsets.ModelViewSet): #implementation for CRUD operations by default.
    serializer_class = UserSerializer
    queryset = User.objects.all()
'''

''' DEPRECATED
def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})
'''

@login_required(login_url='login')
def main(request):
    user_count = User.objects.all().count()
    context = {
        'user_count': user_count,
    }
    return render(request, "index.html", context=context)

@login_required(login_url='login')
def users(request):
    users = User.objects.all()
    context = {
        'users': [user.username for user in users],
    }
    return render(request, "users.html", context=context)


def auth42(request):
    if request.user.is_authenticated:
        return redirect("main")
    code = request.GET.get('code')
    body = {
    'grant_type': 'authorization_code',
    'client_id': os.environ.get('CLIENT_ID'),
    'client_secret': os.environ.get('CLIENT_SECRET'),
    'code': f'{code}',
    'redirect_uri': 'http://localhost:8000/auth42'
    }
    r = requests.post('https://api.intra.42.fr/oauth/token', data=body)

    user = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + r.json()['access_token']})

    user_info = json.dumps(user.json(), indent=4)
    if (User.objects.filter(username=user.json()['login']).exists() == False):
        new_user = User.objects.create(username=user.json()['login'], password=r.json()['refresh_token'])
        new_user.save()
        new_user = authenticate(request, username=user.json()['login'], password=r.json()['refresh_token'])
        login_user(request, new_user)
        return redirect("main")
    else:
        messages.error(request, f"This username is already taken: {user.json()['login']}. C'mon, be more creative!")
        return redirect("login")


def login(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            login = form.cleaned_data['login']
            token = form.cleaned_data['token']
            if (User.objects.filter(username=login).exists()):
                user = User.objects.get(username=login)
                if (user.password == token):
                    if (user is not None):
                        login_user(request, user)
                        messages.success(request, f'You are logged in as {login}')
                        return redirect("main")
                    else:
                        messages.error(request, f"LOGIN FUCKS UP")
                        return redirect("register")
                else:
                    messages.info(request, f"Invalid password or username")
                    return redirect("register")
            else:
                messages.info(request, f"Invalid password or username")
                return redirect("register")
    else:
        form = RegistrationForm(request.POST or None)
        return render(request, "login.html", {'form': form})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            login = form.cleaned_data['login']
            token = form.cleaned_data['token']
            if (User.objects.filter(username=login).exists()):
                messages.error(request, f"This username is already taken: {login}. C'mon, be more creative!")
                form = RegistrationForm(request.POST or None)
                return render(request, "register.html", {'form': form})
            
            elif (token != ""):
                new_user = User.objects.create(username=login, password=token)
                new_user.save()
                profile = Profile.objects.create(user=new_user)
                profile.match_history = json.dumps([{'p1':0,'p2':0,'opponent':'nkahrima'}])
                new_user.profile.save()
                new_user = authenticate(request, username=login, password=token)
                messages.success(request, f"You've successfully registered as {login}!")
                return redirect("main")
        else:
            form = RegistrationForm(request.POST or None)
            return render(request, "register.html", {'form': form})
    else:
        form = RegistrationForm(request.POST or None)
        return render(request, "register.html", {'form': form})

@login_required(login_url='login')
def logout(request):
    logout_user(request)
    return redirect("login")


@login_required(login_url='login')
def profile(request):
    #image_file = request.FILES['image_file'].file.read()
    if request.method == "POST":
        username_form = UsernameForm(request.POST)
        avatar_form = AvatarForm(request.POST, request.FILES)
        if username_form.is_valid() and avatar_form.is_valid():
            print("form is valid")
            if 'change-username' in request.POST:
                new_login = username_form.cleaned_data['login']
                if (User.objects.filter(username=new_login).exists()):
                    print("username already taken")
                    messages.error(request, f"This username is already taken: {new_login}. C'mon, be more creative!")
                    username_form = UsernameForm(request.POST)
                    return render(request, "profile.html", {'form': {username_form, avatar_form}, 'username': request.user.username, 'avatar': Profile.objects.get(user=request.user).avatar})
                else:
                    print("username updated")
                    user = User.objects.get(username=request.user.username)
                    user.username = new_login
                    user.save()
                    messages.success(request, f"You've changed your username to: {new_login}")
            if 'change-avatar' in request.POST:
                print("avatar updated")
                request.user.profile.avatar = avatar_form.cleaned_data['avatar']
                request.user.profile.refresh_from_db()
                request.user.profile.save()
                messages.success(request, f"You've changed your avatar.")
        else:
            print("invalid form")
            username_form = UsernameForm(request.POST)
            messages.error(request, f"INVALID FORM, TRY AGAIN.")
            return render(request, "profile.html", {'form': [username_form, avatar_form], 'username': request.user.username, 'avatar': Profile.objects.get(user=request.user).avatar})
    else:
        print("form is not in post req")
        username_form = UsernameForm(request.POST)
        avatar_form = AvatarForm(request.POST, request.FILES)
        return render(request, "profile.html", {'form': [username_form, avatar_form], 'username': request.user.username, 'match_history': Profile.objects.get(user=request.user).match_history, 'avatar': Profile.objects.get(user=request.user).avatar})


@login_required(login_url='login')
def pollindex(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required(login_url='login')
def searchUser(request, user_name):
    users = User.objects.all()
    user_names = [user.username for user in users]

    if (user_name in user_names):
        return HttpResponse("User you are looking for exists: %s." % user_name)
    else:
        return HttpResponse("THIS USER DOES NOT EXIST")