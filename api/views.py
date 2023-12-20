from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, GameSerializer, ProfileSerializer, GameSerializer, TournamentSerializer
from .models import Game, Profile, Tournament

class LoginViewSet(viewsers.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = 

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
        

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer