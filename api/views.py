from .serializers import UserSerializer, GameSerializer, ProfileSerializer, TournamentSerializer
from .models import Game, Profile, Tournament, User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    try:
        if (User.objects.filter(username=request.data["username"]).exists() == True):
            user = User.objects.get(username=request.data["username"])
            if user.check_password(request.data["password"]):
                token = Token.objects.get_or_create(user=user)
                return Response({
                    'success': True,
                    'token': str(token),
                })
            else:
                return Response({"error": "Invalid password."}, status=401)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        request.user.profile.is_online = False
        request.user.save()

        return Response({'success': True})
    except Token.DoesNotExist:
        return Response({'success': False, "error": "Token not found."}, status=404)
    except Exception as e:
        return Response({'success': False, "error": f"Internal server error: {str(e)}"}, status=500)


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'success': True,})
    return Response({'success': False})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])  # Use TokenAuthentication or the authentication method you prefer
@permission_classes([IsAuthenticated])
def authenticated_test(request):
    user = request.user
    return Response({
        'success': True,
    })
    

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def addfriend(request):
    try:
        user = request.user
        friend = User.objects.get(username=request.data["username"])
        user.profile.friends.append(friend.username)
        friend.profile.friends.append(user.username)
        user.save()
        friend.save()
        return Response({"success": True})
    except:
        return Response({"success": False})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def removefriend(request):
    try:
        user = request.user
        user.profile.friends.remove(request.data["username"])
        user.save()
        return Response({"success": True})
    except:
        return Response({"success": False})
    

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def search(request):
    try:
        if (request.data["searchQuery"] == ""):
            return Response({"success": False})
        
        usernames_list = User.objects.values_list('username', flat=True).filter(username__icontains=request.data["searchQuery"])
        users_data = list()

        for username in usernames_list:
            if username != request.user.username:
                try:
                    user = User.objects.get(username=username)
                    profile = user.profile
                    users_data.append({
                        "username": username,
                        "is_online": profile.is_online,
                    })
                except User.DoesNotExist:
                    # Handle the case where the user object for a username is not found
                    pass
        #users_data = [{"username": username} for username in usernames_list if username != request.user.username]
        return Response({
            "success": True,
            "users": users_data,
            })
    except:
        return Response({"success": False})
    
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
def friendslist(request):
    try:
        friends_list = list()
        friends = request.user.profile.friends
        if (len(friends) == 0):
            return Response({'success': False})
        else:
            for friend_name in friends:
                friend = User.objects.get(username=friend_name)
                if (friend.profile.is_online == True):
                    is_online = True
                else:
                    is_online = False
                friend.save()
                friends_list.append({"username": friend_name, "is_online": is_online})
            return Response({
                'success': True,
                'friends': friends_list,
            })
    except:
        return Response({"success": False})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def create_tournament(request):
    try:
        tournament = Tournament.objects.create(creator = request.user.username)
        tournament.waitlist.append(request.user.username)
        tournament.save()
        request.user.profile.is_gaming = True
        return Response({"success": True, "tournament_id": tournament.tournament_id, "tournament_state": tournament.state}) 
    except:
        return Response({"success": False})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def join_tournament(request):
    try:
        if (Tournament.objects.filter(tournament_id = request.data["tournament_id"]).exists() == True):

            tournament = Tournament.objects.get(tournament_id = request.data["tournament_id"])
            tournament.waitlist.append(request.user.username)
            tournament.invitelist.remove(request.user.username)
            tournament.save()

            if (request.user.username in tournament.waitlist):
                request.user.profile.is_gaming = True
                return Response({"success": True,})
            else:
                print("burası")
                return Response({"success": False,})

        else:
            return Response({"success": False})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({"success": False, "error_message": str(e)})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def invite_tournament(request):
    try:
        if (User.objects.filter(username=request.data["username"]).exists() == True
            and User.objects.get(username=request.data["username"]).profile.is_online == True
            and User.objects.get(username=request.data["username"]).profile.is_gaming == False
            and Tournament.objects.filter(tournament_id = request.data["tournament_id"]).exists() == True): #check state?

            tournament = Tournament.objects.get(tournament_id = request.data["tournament_id"])
            tournament.invitelist.append(request.data["username"])
            tournament.save()

            if (len(tournament.invitelist) == 3):
                return Response({"success": True, "user_count": 3})
            
            return Response({"success": True, "user_count": len(tournament.invitelist), "tournament_id": tournament.tournament_id})
        else:
            return Response({"success": False, 'new': True})
    except:
        return Response({"success": False})

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def start_tournament(request):
    try:
        user = request.user
        all_tournaments = Tournament.objects.all()
        if (all_tournaments):
            for tournament in all_tournaments:
                if (tournament and tournament.invitelist and user.username in tournament.invitelist and user not in tournament.waitlist):
                    return Response({"success": True, "tournament_id": tournament.tournament_id, "tournament_state": tournament.state})
                else:
                    return Response({"success": False})
      
        else:
            return Response({'success': False})
    except:
        return Response({"success": False})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tournament_table(request):
    try:
        tournament = Tournament.objects.get(tournament_id=request.data["tournament_id"])
        if request.user.username in tournament.invitelist:
           tournament.invitelist.remove(request.user.username)
           tournament.waitlist.append(request.user.username)
           tournament.save()

        formatted_users = [{"username": user} for user in tournament.waitlist]

        return Response({
            "success": True,
            "tournament_id": tournament.tournament_id,
            "tournament_state": tournament.state,
            "users": formatted_users,
            "users_length": len(formatted_users),
        })
    except Tournament.DoesNotExist:
        return Response({"success": False, "error": "Tournament not found"})
    except Exception as e:
        return Response({"success": False, "error": str(e)})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_profile(request):
    try:
        is_friend = False
        if (User.objects.filter(username=request.data["username"]).exists() == True):
            user = User.objects.get(username=request.data["username"])
        if (user.username in request.user.profile.friends):
            is_friend = True

        print("ADDFRIEND" + str(user.profile.friends) + str(request.user.profile.friends))
        return Response({
            "success": True,
            "is_friend": is_friend,
            "username": user.username,
            "friends_count": len(user.profile.friends),
            "is_online": user.profile.is_online,
            "match_count": len(user.profile.match_history),
            })
    except:
        return Response({"success": False})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_myprofile(request):
    try:
        user = request.user
        return Response({
            "success": True,
            "username": user.username,
            "friends_count": len(user.profile.friends),
            "match_count": len(user.profile.match_history),
            })
    except:
        return Response({"success": False})


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
def matching(request):
    try:
        user = request.user
        all_games = Game.objects.all()

        users_games = None
        for game in all_games:
            if user.username in game.waitlist and game.state == 0:
                users_games = game
                break
        if users_games is not None:
            if len(users_games.waitlist) < 2:
                return Response({"success": True, "game_id": users_games.game_id, "game_state": users_games.state, "match": False})
            elif len(users_games.waitlist) == 2:
                return Response({"success": True, "game_id": users_games.game_id, "game_state": users_games.state, "match": True})
        else:
            for game in all_games:
                if len(game.waitlist) < 2 :
                    game.waitlist.append(user.username)
                    game.player2 = user.username
                    game.save()
                    return Response({"success": True, "game_id": game.game_id, "game_state": game.state, "match": False})
            new_game = Game.objects.create(player1 = user.username)
            new_game.waitlist.append(user.username)
            new_game.save()
            return Response({"success": True, "game_id": new_game.game_id, "game_state": new_game.state, "match": False})
    except:
        return Response({"success": False})

                

                    
            
    
'''
        if (game and len(game.waitlist) == 2):
            return Response({"success": True, "player": 1, "game_id": game.game_id, "game_pass": 4242, "player_pass": 2121, "game_state": game.state, "match": True})
        if game and len(game.waitlist) < 2:
            if game.player1 == user.username:
                return Response({"success": True, "game_id": new_game.game_id, "game_pass": 4242, "player_pass": 2121, "game_state": new_game.state, "match": False})
            user.profile.is_gaming = True
            user.profile.ready_to_play = True
            if user.username not in game.waitlist:
                game.waitlist.append(user.username)
                game.player2 = user.username
                game.save()
                return Response({"success": True, "player": 1, "game_id": game.game_id, "game_pass": 4242, "player_pass": 2121, "game_state": game.state, "match": True})
            else:
                return Response({'success':False})
        elif game and user.username not in game.waitlist:
            new_game = Game.objects.create(player1 = user.username)
            new_game.waitlist.append(user.username)
            return Response({"success": True, "game_id": new_game.game_id, "game_pass": 4242, "player_pass": 2121, "game_state": new_game.state, "match": False})
        else:
            return Response({"success": False})'''
    

'''

def get_user_games(user):
    games = Game.objects.all(player1_token=user.profile.token).append(Game.objects.all(player2_token=user.profile.token))
    return games


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