from .serializers import UserSerializer, GameSerializer, ProfileSerializer, TournamentSerializer
from .models import Game, Profile, Tournament
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Profile.objects.create(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def authenticate_user(request):
    # Use the ObtainAuthToken view for token generation
    obtain_auth_token_view = ObtainAuthToken.as_view()
    response = obtain_auth_token_view(request)

    if response.status_code == 200:
        # Authentication successful, return the token
        return Response({'token': response.data.get('token')})
    else:
        # Authentication failed, return an error response
        return Response({'error': 'Unable to authenticate with provided credentials'}, status=response.status_code)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])  # Use TokenAuthentication or the authentication method you prefer
@permission_classes([IsAuthenticated])
def authenticated_test(request):
    user = request.user
    return Response({'message': f'Hello, {user.username}! You are authenticated.'})

'''
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


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Use the obtain_auth_token view for token generation
        response = obtain_auth_token(request)
        # You can customize the response if needed
        # For example, you might want to return additional user information
        return Response({'token': response.data['token'], 'user_id': request.user.id})

@api_view(["POST"])
def login(request):
    django_request = request._request
    response = obtain_auth_token(django_request)
    return Response({'token': response.data['token'], 'user_id': django_request.user.id})
    response = obtain_auth_token(request)
    return Response({'token': response.data['token'], 'user_id': request.user.id})
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



def get_user_games(user):
    games = Game.objects.all(player1_token=user.profile.token).append(Game.objects.all(player2_token=user.profile.token))
    return games


@api_view(["GET"]) #token password olarak döndü?
def userlist(request): # responselar belirli değil, spesifikleştirilecek
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def friendslist(request):
    profile = Profile.objects.get(token=request.data["token"])
    if (profile.friends != 0):
        return Response({
            "success": True,
            "friends": profile.friends
        })
    else:
        return Response({
            "success": False,
        })

@api_view(["POST"])
def addfriend(request):
    try:
        profile = Profile.objects.get(token=request.data["token"])
        profile.friends.append(request.data["friend"])
        profile.save()
        return Response({"success": True})
    except:
        return Response({"success": False})

@api_view(["POST"])
def removefriend(request):
    try:
        profile = Profile.objects.get(token=request.data["token"])
        profile.friends.remove(request.data["friend"])
        profile.save()
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

'''
'''
@api_view(["GET"]) #create game iboya atılacak, {game_id, player1_token, player2_token}
def creategame(request):
    game = Game.objects.create();
    #oyun oluşturan ve oyunu oynayan herkesin is_gaming'i True olmalı.
    post_data = {'game_id': game.id, 'player1_token': '', 'player2_token': ''}
    response = requests.post('http://example.com', data=post_data)
    return Response(response)'''
'''

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
    profile = Profile.objects.get(token=request.data["token"])
    if (profile.user_id == User.objects.get(username=request.data["username"]).id):
        #my_profile
        user = User.objects.get(token=request.data["token"])
        match_history = get_user_games(user)
        return Response({
            "success":True,
            "username": user.username,
            "friends_count": len(user.profile.friends),
            "avatar": user.profile.avatar,
            "online_status": user.profile.is_online,
            "match_history": match_history,
        })
    else:
        #other_profile
        user = User.objects.get(username=request.data["username"])
        match_history = get_user_games(user)
        return Response({
            "success":True,
            "username": user.username,
            "friends_count": len(user.profile.friends),
            "avatar": user.profile.avatar,
            "online_status": user.profile.is_online,
            "match_history": match_history,
        })
    
################# TOURNAMENT ENDPOINTS -START- #################
@api_view(["POST"])
def createTournament(request):
    try:
        tournament = Tournament.objects.create(creator_token=request.data["token"])
        tournament.waitlist.append(request.data["token"])
        tournament.save()
        user = Profile.objects.filter(token=request.data["token"])
        user.is_gaming = True
        return Response({
            "success":True,
            "waiting_list": len(tournament.waitlist),
            "tournament_id": tournament.tournament_id,
        })
    except:
        return Response({
            "success":False,
        })


@api_view(["POST"])
def inviteTournament(request):
    try:
        if (User.objects.filter(username=request.data["username"]).exists() == False):
            return Response({
                "success":False,
                "error":"Username not found."
            })
        else:
            friend = User.objects.get(username=request.data["username"])
            if (friend.profile.is_online == False):
                return Response({
                    "success":False,
                    "error":"User is offline."
                })
            else:
                user = User.objects.get(token=request.data["token"])
                tournament = Tournament.objects.last(creator_token=user.profile.token)
                return Response({
                    "success":True,
                    "count": len(tournament.waitlist),
                    "tournament_id": tournament.tournament_id,
                    "token": friend.profile.token,
            })
    except:
        return Response({
            "success":False,
            "error":"Something went wrong.",
        })

@api_view(["POST"])
def acceptTournament(request):
    try:
        tournament = Tournament.objects.get(tournament_id=request.data["tournament_id"])
        tournament.waitlist.append(request.data["token"])
        tournament.save()
        return Response({
            "success":True,
            "waiting_list": tournament.waitlist,
            "count": len(tournament.waitlist), #tournament players count
            "tournament_id": 0, #tournament id
        })
    except:
        return Response({
            "success":False,
            "error":"Something went wrong."
        })
################# TOURNAMENT ENDPOINTS -END- #################   
    
@api_view(["POST"])
def updateprofile(request):
    if(Profile.objects.filter(request.data["token"]).exists()):
        try:
            profile = Profile.objects.get(token=request.data["token"])
            if (request.data["username"] != "" and User.objects.filter(username=request.data["username"]).exists() == False):
                profile.user.username = request.data["username"]
            if (request.data["avatar"] != ""):
                profile.avatar = request.data["avatar"]
            if (request.data["lan"] != "" and (request.data["lan"] == "tr" or request.data["lan"] == "en" or request["lan"] == "fr")):
                profile.lan = request.data["lan"]
            profile.save()
            return Response({
                "success":True,
            })
        except:
            return Response({
                "success":False,
            })

'''