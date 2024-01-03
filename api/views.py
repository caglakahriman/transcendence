from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, GameSerializer, ProfileSerializer, TournamentSerializer
from .models import Game, Profile, Tournament
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth import authenticate


@api_view(['POST'])
def register(request):
    if (User.objects.filter(username=request.data["username"]).exists()):
        return Response({"error": "Username already exists."})
    else:
        try:
            user = User.objects.create_user(username=request.data["username"])
            user.set_password(request.data["password"])
            user.save()
            return Response({
                "success": True,
            })   
        except:
            return Response({
                "success": False,
            })


@api_view(["POST"])
def login(request):
    if (User.objects.filter(username=request.data["username"]).exists()):
        try:
            user = User.objects.get(username=request.data["username"])
            user.check_password(request.data["password"])
            return Response({
                "token":user.profile.token,
                "success":True,
                "language":user.profile.lan,
            })
        except:
            return Response({"success": False})
    else:
        return Response({"error": "User not found."})

@api_view(["GET"]) #token password olarak döndü?
def userlist(request): # responselar belirli değil, spesifikleştirilecek
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
    try:
        user = User.objects.get(token=request.data["token"])
        friends = user.profile.friends
        friends.append(request.data["friend"])
        user.profile.friends = friends
        user.save()
        return Response({"success": True})
    except:
        return Response({"success": False})

@api_view(["POST"])
def removefriend(request):
    try:
        user = User.objects.get(token=request.data["token"])
        friends = user.profile.friends
        friends.remove(request.data["friend"])
        user.profile.friends = friends
        user.save()
        return Response({"success": True})
    except:
        return Response({"success": False})

@api_view(["POST"])
def updatename(request):
    user = User.objects.get(token=request.data["token"])
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
    user = User.objects.get(token=request.data["token"])
    user.profile.lan = request.data["lan"]
    user.save()
    return Response({"success": "Profile updated."})

@api_view(["POST"])
def updateonline(request):
    user = User.objects.get(token=request.data["token"])
    user.profile.is_online = request.data["is_online"]
    user.save()
    return Response({"success": "Online status changed."})

@api_view(["POST"])
def updatestats(request):
    user = User.objects.get(token=request.data["token"])
    user.profile.total_played = request.data["total_played"]
    user.profile.wins = request.data["wins"]
    user.profile.losses = request.data["losses"]
    user.save()
    return Response({"success": "Stats updated."})

@api_view(["GET"])
def getuserstats(request):
    games = Game.objects.all(player1_token=request.data["token"]).append(Game.objects.all(player2_token=request.data["token"]))
    return Response(games)

@api_view(["GET"]) #create game iboya atılacak, {game_id, player1_token, player2_token}
def creategame(request):
    post_data = {'player1_token': '', 'player2_token': ''}
    response = requests.post('http://example.com', data=post_data)
    return Response(response)

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
def get_profile(request):
    if (request.data["token"] == request.user.profile.token):
        #my_profile
        user = request.user
        return Response({
            "success":True,
            "username": user.username,
            "friends_count": len(user.profile.friends),
            "avatar": user.profile.avatar,
            "online_status": user.profile.is_online,
            "match_history": user.profile.match_history,
        })
    else:
        #other_profile
        profile = Profile.objects.get(token=request.data["token"])
        user_id = profile.user_id
        user = User.objects.get(id=user_id)
        return Response({
            "success":True,
            "username": user.username,
            "friends_count": len(profile.friends),
            "avatar": profile.avatar,
            "online_status": profile.is_online,
            "match_history": user.profile.match_history,
        })

@api_view(["POST"])
def invite(request):
    friend = User.objects.get(username=request.data["username"])
    if (friend.profile.is_online == False):
        return Response({
            "success":False,
            "error":"User is offline."
        })
    else:
        return Response({
            "success":True,
            "count": 0, #tournament players count
            "tournament_id": 0, #tournament id
            "token": friend.profile.token,
        })


@api_view(["POST"])
def createtournament(request):
    try:
        tournament = Tournament.objects.create(creator_nickname=request.data["nickname"], creator_username=request.data["token"])
        tournament.save()
        return Response({
            "success":True,
            "waiting_list": tournament.waitlist,
            "tournament_id": tournament.tournament_id,
        })
    except:
        return Response({
            "success":False,
            "error":"Something went wrong."
        })