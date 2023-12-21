from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, GameSerializer, ProfileSerializer, GameSerializer, TournamentSerializer
from .models import Game, Profile, Tournament
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if (serializer.is_valid()):
        if (User.objects.filter(username=request.data["username"]).exists()):
            return Response({"error": "Username already exists."})
        else:
            serializer.save()
    else:
        return Response({"error": "Invalid data."})

@api_view(["GET"])
def login(request):
    if (User.objects.filter(username=request.data["username"]).exists()):
        user = User.objects.get(username=request.data["username"])
        if (user.password == request.data["password"]):
            return Response({
                "username": user.username,
                "token": user.profile.token,
            })
        else:
            return Response({"error": "Wrong password."})
    else:
        return Response({"error": "User not found."})

@api_view(["GET"])
def userlist(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def friendslist(request):
    user = User.objects.get(token=request.user.profile.token)
    friends = user.profile.friends
    return Response(friends)

@api_view(["POST"])
def addfriend(request):
    user = User.objects.get(token=request.user.profile.token)
    friends = user.profile.friends
    friends.append(request.data["friend"])
    user.profile.friends = friends
    user.save()
    return Response({"success": "Friend added."})

@api_view(["POST"])
def removefriend(request):
    user = User.objects.get(token=request.user.profile.token)
    friends = user.profile.friends
    friends.remove(request.data["friend"])
    user.profile.friends = friends
    user.save()
    return Response({"success": "Friend removed."})

@api_view(["POST"])
def updatename(request):
    user = User.objects.get(token=request.user.profile.token)
    user.profile.user.username = request.data["username"]
    user.save()
    return Response({"success": "Username updated."})

@api_view(["POST"])
def updateavatar(request):
    user = User.objects.get(token=request.user.profile.token)
    user.profile.avatar = request.data["avatar"]
    user.save()
    return Response({"success": "Avatar updated."})

@api_view(["POST"])
def updatelang(request):
    user = User.objects.get(token=request.user.token)
    user.profile.lan = request.data["lan"]
    user.save()
    return Response({"success": "Profile updated."})

@api_view(["POST"])
def updateonline(request):
    user = User.objects.get(token=request.user.token)
    user.profile.is_online = request.data["is_online"]
    user.save()
    return Response({"success": "Online status changed."})

@api_view(["POST"])
def updatestats(request):
    user = User.objects.get(token=request.user.token)
    user.profile.total_played = request.data["total_played"]
    user.profile.wins = request.data["wins"]
    user.profile.losses = request.data["losses"]
    user.save()
    return Response({"success": "Stats updated."})

@api_view(["GET"])
def getuserstats(request):
    games = Game.objects.all(player1_token=request.user.token).append(Game.objects.all(player2_token=request.user.token))
    return Response(games)

@api_view(["POST"])
def creategame(request):
    serializer = GameSerializer(data=request.data)
    if (serializer.is_valid()):
        serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
def createtournament(request):
    serializer = TournamentSerializer(data=request.data)
    if (serializer.is_valid()):
        serializer.save()
    return Response(serializer.data)

@api_view(["GET"])
def gettournaments(request):
    tournaments = Tournament.objects.all(state=False)
    serializer = TournamentSerializer(tournaments, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getgames(request):
    games = Game.objects.all(state=False)
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getuser(request):
    profile = Profile.objects.get(token=request.data["token"])
    user_id = profile.user_id
    user = User.objects.get(id=user_id)
    return Response({
        "token":profile.token,
        "username":user.username,
    })