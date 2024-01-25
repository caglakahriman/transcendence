from .serializers import UserSerializer, GameSerializer, ProfileSerializer, TournamentSerializer, AvatarSerializer
from .models import Game, Profile, Tournament, User, Avatar
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
import random
from urllib.parse import urljoin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
import requests

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    try:
        if (User.objects.filter(username=request.data["username"]).exists() == True):
            user = User.objects.get(username=request.data["username"])
            if user.check_password(request.data["password"]):
                token = Token.objects.get_or_create(user=user)
                user.profile.is_online = True
                user.save()
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
        
        backend_url = request.build_absolute_uri('/')
        full_avatar_url = urljoin(backend_url, user.avatar.avatar.url)

        return Response({
            "success": True,
            "is_friend": is_friend,
            "username": user.username,
            "avatar": full_avatar_url,
            "is_online": user.profile.is_online,
            "match_count": len(user.profile.match_history),
            "friends_count": len(user.profile.friends),
            "matches_win": user.profile.wins,
            })
    except:
        return Response({"success": False})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_myprofile(request):
    try:
        user = request.user

        backend_url = request.build_absolute_uri('/')
        full_avatar_url = urljoin(backend_url, user.avatar.avatar.url)

        return Response({
            "success": True,
            "username": user.username,
            "avatar": full_avatar_url,
            "friends_count": len(user.profile.friends),
            "match_count": len(user.profile.match_history),
            "matches_win": user.profile.wins,
        })
    except:
        return Response({"success": False})


def get_avatar_binary(request):
    user = request.user
    avatar = user.profile.avatar  # varsayılan olarak kullanıcının avatarını alın
    if avatar:
        # Eğer avatar varsa, binary verileri alın ve HTTP response olarak döndürün
        return HttpResponse(avatar.read(), content_type='image/jpeg')  # veya content_type='image/png' vb. kullanabilirsiniz
    else:
        # Eğer avatar yoksa, uygun bir hata durumu döndürün
        return HttpResponse(status=404)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_avatar(request):
    user = request.user

    try:
        avatar = Avatar.objects.get(user=user)
    except ObjectDoesNotExist:
        avatar = Avatar.objects.create(user=user)

    uploaded_file = request.FILES.get('photo')
    if uploaded_file:
        avatar.avatar = uploaded_file
        avatar.save()
        return Response({"success": True,})
    else:
        return Response({"success": False})

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user = request.user
        profile = user.profile

        print("username", request.data["username"])
        updated_data = request.data

        if 'password' in updated_data:
            user.password = make_password(updated_data['password'])

        if User.objects.exclude(pk=user.pk).filter(username=request.data["username"]).exists():
            return Response({"success": False, "error": "Username is already in use by another user."})


        # Diğer güncelleme verilerini profilde güncelle
        profile.user.username = updated_data.get('username', profile.user.username)
        profile.lan = updated_data.get('language', profile.lan)

        # Profili kaydet
        user.save()
        profile.save()

        return Response({"success": True, "message": "Profile updated successfully."})
    except Exception as e:
        return Response({"success": False, "error": str(e)})
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_avatar(request):
    user = request.user
    avatar = get_object_or_404(Avatar, user=user)
    
    return JsonResponse({
        'success': True,
        'avatar_name': avatar.avatar.name,  # Provide the filename
        'avatar_path': avatar.avatar.url,
    })


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
def matching(request):
    try:
        user = request.user
        all_games = Game.objects.all()

        users_games = None
        print('user.username: ', user.username)
        for game in all_games:
            if user.username in game.waitlist and game.state == 0:
                users_games = game
                print('hey')
                break
        if users_games is not None:
            print('true')
            if len(users_games.waitlist) < 2:
                return Response({"success": True, "playerpass": user.profile.id, "game_id": users_games.game_id, "game_state": users_games.state, "match": False})
            elif len(users_games.waitlist) == 2:
                player_1 = users_games.waitlist[0]
                player_2 = users_games.waitlist[1]
                user_player1 = User.objects.get(username=player_1)
                user_player2 = User.objects.get(username=player_2)

                print('users_games.player1: ', users_games.player1)
                print('users_games.player1 id : ', user.profile.id)
                mydata = {
                    'game_id': str(users_games.game_id),
                    'password': '4242',
                    'password_p1': user_player1.id,
                    'password_p2': user_player2.id,
                    'private': 1,
                }
                print('mydata:', mydata)
                try:
                    game_response = requests.post('http://apipong.ftpong.duckdns.org/api/new_game/', data=mydata)
                    print('game_response: ', game_response.text)
                except requests.exceptions.RequestException as e:
                    print('Hata:', e)

                if game_response.ok:
                    return Response({
                        "success": True,
                        "game_pass": '4242',
                        "player": (int(user.profile.id != users_games.player1.profile.id) + 1),
                        "player_pass": user.profile.id,
                        "game_id son": str(users_games.game_id),
                        "game_state": users_games.state,
                        "match": True,
                    })
                else:
                    return Response({"success": False})
                
                    
        else:
            for game in all_games:
                if len(game.waitlist) < 2 :
                    game.waitlist.append(user.username)
                    game.player2 = user.username
                    game.save()
                    return Response({"success": True, "playerpass": user.profile.id, "game_id": game.game_id, "game_state": game.state, "match": False})
            new_game = Game.objects.create(player1 = user.username)
            new_game.waitlist.append(user.username)
            new_game.save()
            return Response({"success": True, "playerpass": user.profile.id, "game_id": new_game.game_id, "game_state": new_game.state, "match": False})
    except:
        print('false')
        return Response({"success": False})

                
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def head_tail(request):
    try:
        type_1_game_list = Game.objects.filter(type=1)
        if type_1_game_list:
            for type_1_game in type_1_game_list:
                if (
                    type_1_game.player1 == request.user.username
                    and type_1_game.player2 != '' and type_1_game.player2 != None
                    and type_1_game.state == 0
                ):
                    type_1_game.state = 1
                    type_1_game.save()
                    return Response({"success": True, "game_id": type_1_game.game_id,})
                elif (type_1_game.player1 == request.user.username and (type_1_game.player2 is None or type_1_game.player2 == '')):
                    return Response({"success": False})
                elif (
                    type_1_game.player1 != request.user.username
                    and (type_1_game.player2 is None or type_1_game.player2 == '')
                    and type_1_game.state == 0
                ):
                    type_1_game.player2 = request.user.username
                    type_1_game.save()
                    return Response({"success": True, "game_id": type_1_game.game_id,})
            new_game = Game.objects.create(player1=request.user.username, type=1)
            new_game.save()
            return Response({"success": False})
        else:
            new_game = Game.objects.create(player1=request.user.username, type=1)
            new_game.save()
            return Response({"success": False})
    except Game.DoesNotExist:
        return Response({"success": False})


""" """

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_head_tail(request):
    try:
        print("check_head_tail")
        game = Game.objects.get(game_id=request.data["game_id"])
        user = request.user
        if (game.state == 4 or game.state == 5):
            print("1")
            print("game.player1: ", game.player1)
            print("game.player2: ", game.player2)
            if (game.player1 == request.user.username and game.player2_score != '' and game.player2_score != None):
                print("Player1_score: ", game.player1_score)
                print("Player2_score: ", game.player2_score)
                if (game.player1_score >= game.player2_score):
                    print("2")
                    print("player 1 in scoru büyük player 2 ninkinden aşağıda")
                    print("Player1_score: ", game.player1_score)
                    print("Player2_score: ", game.player2_score)
                    print("ve player 1 kazanır")
                    game.winner = user.profile.id
                    game.save()
                    print("1save")
                    return Response({"success": True, "winner": 1})
                else:
                    print("3")
                    return Response({"success": True,  "lose": 1})
            elif (game.player2 == request.user.username and game.player1_score != '' and game.player1_score != None):
                print("Player1_score: ", game.player1_score)
                print("Player2_score: ", game.player2_score)
                if (game.player2_score >= game.player1_score):
                    print("4")
                    print("player 2 in scoru büyük player 1 ninkinden aşağıda")
                    print("Player1_score: ", game.player1_score)
                    print("Player2_score: ", game.player2_score)
                    print("ve player 2 kazanır")
                    game.winner = user.profile.id
                    game.save()
                    print("2save")
                    return Response({"success": True, "winner": 1})
                else:
                    print("5")
                    return Response({"success": True, "lose": 1})
            else:
                print("6")
                print("game.player1 again : ", game.player1)
                print("game.player2 again: ", game.player2)
                return Response({"success": True, "again": 1})
        else:
            print("7")
            return Response({"success": False})
    except:
        return Response({"success": False})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def head_tail_race(request):
    try:
        random_value = random.randint(4, 5)
        game = Game.objects.get(game_id=request.data["game_id"])
        if (game.state == 1):
            game.state = random_value
            game.save()
        headclickcount = request.data["headClickCount"]
        tailclickcount = request.data["tailClickCount"]
        if (game.state == 4 and game.player1 == request.user.username):#head_score
            game.player1_score = headclickcount
            game.save()
            print("head_score player 1", game.player1_score)
            print("player 2  id : ", game.player2)
            return Response({"success": True, "notset": 2})
        elif (game.state == 5 and  game.player1 == request.user.username): #tail_score
            game.player1_score = tailclickcount
            game.save()
            print("tail_score player 1", game.player1_score)
            print("player 2  id : ", game.player1)
            return Response({"success": True, "notset": 2})
        elif (game.state == 4 and game.player2 == request.user.username):
            game.player2_score = headclickcount
            game.save()
            print("head_score player 2", game.player2_score)
            print("player 2  id : ", game.player2)
            return Response({"success": True, "notset": 2})
        elif (game.state == 5 and game.player2 == request.user.username):
            game.player2_score = tailclickcount
            game.save()
            print("tail_score player 2", game.player2_score)
            print("player 2  id : ", game.player2)
            return Response({"success": True, "notset": 2})
    except:
        return Response({"success": False})

            
    
        """ if (random_value == 0): #head
           if (headclickcount >= tailclickcount and game.player1 == request.user.username):
               game.player1_score == headclickcount
               game.save()
               if (game.player2_score != '' and game.player2_score != None):
                   if (game.player1_score > game.player2_score):
                       game.state = 2
                       game.save()
                       return Response({"success": True, "winner": game.player1})
           if (headclickcount >= tailclickcount and game.player2 == request.user.username):
                game.player2_score == headclickcount
                game.save()
                if (game.player1_score != '' and game.player1_score != None):
                    if (game.player2_score > game.player1_score):
                        game.state = 2
                        game.save()
                        return Response({"success": True, "winner": game.player2})
           else:
               return Response ({"success": False})
        else:                   #tail
            if (tailclickcount >= headclickcount and game.player1 == request.user.username):
                game.player1_score == tailclickcount
                game.save()
                if (game.player2_score != '' and game.player2_score != None):
                    if (game.player1_score > game.player2_score):
                        game.state = 2
                        game.save()
                        return Response({"success": True, "winner": game.player1})
                    else:
                        return Response({"success": False})
                else:
                    return Response({"success": False})
            if (tailclickcount >= headclickcount and game.player2 == request.user.username):
                game.player2_score == tailclickcount
                game.save()
                if (game.player1_score != '' and game.player1_score != None):
                    if (game.player2_score > game.player1_score):
                        game.state = 2
                        game.save()
                        return Response({"success": True, "winner": game.player2})
            else:
                return Response({"success": False, "error": "Something went wrong."}) """
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