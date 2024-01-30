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
import json

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    try:
        if (User.objects.filter(username=request.data["username"]).exists() == True):
            user = User.objects.get(username=request.data["username"])
            if user.check_password(request.data["password"]):
                token = Token.objects.get_or_create(user=user)
                user.profile.is_online = True
                user.profile.save()
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
        tournament.state = 1
        tournament.save()
        request.user.profile.is_gaming = True
        request.user.profile.save()
        return Response({"success": True, "tournament_id": tournament.tournament_id, "tournament_state": tournament.state}) 
    except:
        return Response({"success": False})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def join_tournament(request):
    try:
        if (Tournament.objects.filter(tournament_id = request.data["tournament_id"]).exists() == True):

            tournament = Tournament.objects.get(tournament_id = request.data["tournament_id"])
            if request.user.username in tournament.invitelist:
                tournament.invitelist.remove(request.user.username)
            if request.user.username in tournament.waitlist:
                tournament.waitlist.remove(request.user.username)
            tournament.waitlist.append(request.user.username)
            tournament.save()
            if (request.user.username in tournament.waitlist):
                request.user.profile.is_gaming = True
                request.user.profile.save()
                return Response({"success": True})
            else:
                return Response({"success": False})

        else:
            return Response({"success": False, "message": "Turnuva Bulunamadı. Sanırım geç kaldın :("})
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
            and Tournament.objects.filter(tournament_id = request.data["tournament_id"]).exists() == True
            and request.data["username"] != request.user.username):
            tournament = Tournament.objects.get(tournament_id = request.data["tournament_id"])
            tournament.invitelist.append(request.data["username"])
            #tournament.state += 1
            tournament.save()

            if (len(tournament.invitelist) == 3 or len(tournament.waitlist) == 4):
                tournament.state = 1
                return Response({"success": True, "user_count": 3})
            return Response({"success": True, "user_count": len(tournament.invitelist), "tournament_id": tournament.tournament_id})
        else:
            response_data = {"success": False}

            if not User.objects.filter(username=request.data["username"]).exists():
                response_data['message'] = "Kullanıcı mevcut değil. Lütfen başka bir kullanıcı adı girin."
            elif not User.objects.get(username=request.data["username"]).profile.is_online:
                response_data['message'] = "Kullanıcı çevrimiçi değil. Lütfen başka bir kullanıcı adı girin."
            elif User.objects.get(username=request.data["username"]).profile.is_gaming:
                response_data['message'] = "Kullanıcı şu anda bir oyun oynuyor. Lütfen başka bir kullanıcı adı girin."
            elif not Tournament.objects.filter(tournament_id=request.data["tournament_id"]).exists():
                response_data['message'] = "Turnuva mevcut değil. Lütfen bir önceki sayfaya dönün ve tekrar deneyin."
            return Response(response_data)
    except:
        return Response({"success": False, "Message": "Bişeyler ters gitti. Lütfen tekrar deneyin."})

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def start_tournament(request):
    try:
        user = request.user
        all_tournaments = Tournament.objects.all()
        if (all_tournaments):
            for tournament in all_tournaments:
                print("tournament", tournament)
                if (tournament and tournament.invitelist and user.username in tournament.invitelist and user not in tournament.waitlist and tournament.state == 1):
                    return Response({"success": True, "tournament_id": tournament.tournament_id, "tournament_state": tournament.state, "invitelist": True})
                elif (tournament and tournament.waitlist and user.username in tournament.waitlist and tournament.state == 1):
                    return Response({"success": True, "tournament_id": tournament.tournament_id, "tournament_state": tournament.state, "waitlist": True})
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
        """ if request.user.username in tournament.invitelist:
           tournament.invitelist.remove(request.user.username)
           tournament.waitlist.append(request.user.username)
           tournament.save() """

        formatted_users = [{"username": user} for user in tournament.waitlist]

        return Response({
            "success": True,
            "tournament_id": tournament.tournament_id,
            "tournament_state": tournament.state,
            "users": formatted_users,
            "users_length": len(formatted_users),
            "me" : request.user.username,
        })
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
        profile = user.profile
        match_history = profile.match_history

        result_list_type_0 = []
        result_list_type_1 = []
        result_list_type_4 = []

        for game_id, info in match_history.items():
          
            if (info["type"] == 0):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_0.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })
            elif (info["type"] == 1):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_1.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })
            elif (info["type"] == 4):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_4.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })
        print("len ", len(result_list_type_4))
        response_data = {
            "success": True,
            "username": user.username,
            "is_friend": is_friend,
            "avatar": full_avatar_url,
            "is_online": user.profile.is_online,
            "friends_count": len(profile.friends),
            "matches_win": profile.wins,
            "match_count": len(profile.match_history),
            "match_length_type_0": len(result_list_type_0),
            "match_length_type_1": len(result_list_type_1),
            "tournament_cup_count": len(result_list_type_4),
            "matches_type_0": result_list_type_0,
            "matches_type_1": result_list_type_1,
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"success": False, "error_message": str(e)})
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_myprofile(request):
    try:
        user = request.user
        backend_url = request.build_absolute_uri('/')
        full_avatar_url = urljoin(backend_url, user.avatar.avatar.url)
        profile = user.profile
        match_history = profile.match_history

        result_list_type_0 = []
        result_list_type_1 = []
        result_list_type_4 = []

        for game_id, info in match_history.items():
          
            if (info["type"] == 0):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_0.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })
            elif (info["type"] == 1):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_1.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })
            elif (info["type"] == 4):
                date = info["date"]
                opponent = info["player1"] if info["player1"] != user.username else info["player2"]
                outcome = "W" if info["winner"] == profile.id else "L"
                
                result_list_type_4.append({
                    "date": date,
                    "opponent": opponent,
                    "outcome": outcome,
                })

        response_data = {
            "success": True,
            "username": user.username,
            "avatar": full_avatar_url,
            "friends_count": len(profile.friends),
            "matches_win": profile.wins,
            "match_count": len(profile.match_history),
            "match_length_type_0": len(result_list_type_0),
            "match_length_type_1": len(result_list_type_1),
            "tournament_cup_count": len(result_list_type_4),
            "matches_type_0": result_list_type_0,
            "matches_type_1": result_list_type_1,
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"success": False, "error_message": str(e)})


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

@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def clean_tournament(request):
    try:
        user = request.user

        tournamet = Tournament.objects.get(tournament_id=request.data["tournament_id"])
        if (tournamet):
            if user.username in tournamet.waitlist:
                tournamet.waitlist.remove(user.username)
                tournamet.save()
                return Response({"success": True})
        else:
            return Response({"success": False})
    except:
        return Response({"success": False})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tournament_winner(request):
    try:
        user = request.user
        print("username", user.username)
        tournament = Tournament.objects.get(tournament_id=request.data["tournament_id"])
        str_tournament_id = str(tournament.tournament_id)
        tournament_id = str_tournament_id.split('-')[0]
        user_profile = user.profile
        if (tournament):
            print("I am winner 1", user.username)
            print("I am winner 2", tournament_id)
            print("if içi")
            if (user.username in tournament.waitlist):
                tournament.waitlist.remove(user.username)
            print("if içi 2")
            tournament.state = 7
            tournament.save()
            print("if içi 3.33")
            print("tournemenet winner1", tournament.winner1)
            print("tournemenet winner2", tournament.winner2)
            print("tournament_id", tournament_id)
            if (tournament.winner1 is None or tournament.winner1 == '' or tournament.winner1 == None):
                tournament.winner1 = user.username
                tournament.winner2 = tournament_id
                tournament.save()
                new_game = Game.objects.create(player1 = user.username)

                new_game.player1 = user.username
                print("if içi 4.0")
                new_game.player2 = tournament_id
                print("if içi 4.1")
                new_game.type = 7
                new_game.state = 1
                new_game.save()
                print("if içi 4")
                url = "http://pongapi.ftpong.duckdns.org/api/new_game"
                mydata = {
                    'gameid': str(new_game.game_id),
                    'password': '4243',
                    'password_p1': str(user.username),
                    'password_p2': str(tournament_id),
                    'private': True,
                }
                try:
                    game_response = requests.post(url, json=mydata)
                except requests.exceptions.RequestException as e:
                    print('Hata:', e)
                print("game response beign match", game_response)
                if game_response.status_code == 201:
                    print("201 RETURN")
                    return Response({
                        "success": True,
                        "game_pass": '4243',
                        "player": 1,
                        "player_pass": str(user.username),
                        "game_id": str(new_game.game_id),
                        "game_state": new_game.state,
                        "match": True,
                    })
                elif game_response.status_code == 409:
                    return Response({"success": False, "response": 409})
                elif game_response.status_code == 503:
                    print(game_response.text)
                    print("5000000000333")
                    return Response({"success": False, "response": 503})
                return Response({"success": True, "player1": user.username , "player2": tournament_id})
            elif (tournament.winner2 == tournament_id):
                print("if içi 5")
                tournament.winner2 = user.username
                tournament.save()

                print("if içi 6")
                new_game = Game.objects.get(player2 = tournament_id)
                print("GAMEE İNFO", new_game)
                print("if içi 7")
                new_game.player2 = user.username
                new_game.state = 2
                new_game.save()

                return Response(
                    {
                        "success": True,
                        "game_pass": '4243',
                        "player": 2,
                        "player_pass": str(tournament_id),
                        "game_id": str(new_game.game_id),
                        "game_state": new_game.state,
                        "match": True,
                    }
                )
            else:
                print("if içi 8")
                return Response({"success": False})
        else:
            print("son else")
            return Response({"success": False})
    except Exception as e:
        print("except", e)
        return Response({"success": False})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def game_info_back(request):
    try:
        user = request.user
        user_profile = user.profile
        current_match_history = user_profile.match_history

        get_game = Game.objects.get(game_id=request.data["game_id"])
        if (request.data["tournament_id"]):
            tournament = Tournament.objects.get(tournament_id=request.data["tournament_id"])


        get_game.state = 2
        if (get_game.type != 4 and get_game.type != 7):
            get_game.type = 0
        if (get_game.type == 7):
            pass
        get_game.save()
        if (get_game.player1_score != '' and get_game.player1_score != None and get_game.player2_score != '' and get_game.player2_score != None):
            get_game.player1_score = request.data["player1_score"]
            get_game.player2_score = request.data["player2_score"]
            get_game.save()
        if (get_game.player1 == user.username):
            if (get_game.player1_score > get_game.player2_score):
                get_game.winner = user_profile.id
                user_profile.wins += 1
                user_profile.is_gaming = False
                if (request.data["tournament_id"]):
                    tournament.overall_winner = user.username
                    tournament.save()
                try:
                    new_game_data = {
                    'game_id': str(get_game.game_id),
                    'player1': get_game.player1,
                    'player2': get_game.player2,
                    'player1_score': get_game.player1_score,
                    'player2_score': get_game.player2_score,
                    'winner': get_game.winner,
                    'state': get_game.state,
                    'type': get_game.type,
                    'date': get_game.date.strftime('%Y-%m-%d'),
                    }
                    current_match_history[str(get_game.game_id)] = new_game_data
                except Exception as e:
                    print("except", e)
                user_profile.match_history = current_match_history
                user_profile.save()
                get_game.save()
                return Response({"success": True, "winner": 1, "type": get_game.type})
            else:
                user_profile.losses += 1
                user_profile.is_gaming = False
                try:
                    new_game_data = {
                    'game_id': str(get_game.game_id),
                    'player1': get_game.player1,
                    'player2': get_game.player2,
                    'player1_score': get_game.player1_score,
                    'player2_score': get_game.player2_score,
                    'winner': get_game.winner,
                    'state': get_game.state,
                    'type': get_game.type,
                    'date': get_game.date.strftime('%Y-%m-%d'),
                    }
                    current_match_history[str(get_game.game_id)] = new_game_data
                except Exception as e:
                    print("except", e)
                user_profile.match_history = current_match_history
                user_profile.save()
                return Response({"success": True, "lose": 1, "type": get_game.type})
        elif (get_game.player2 == user.username):
            if (get_game.player2_score > get_game.player1_score):
                get_game.winner = user_profile.id
                user_profile.wins += 1
                user_profile.is_gaming = False
                if (request.data["tournament_id"]):
                    tournament.overall_winner = user.username
                    tournament.save()
                try:
                    new_game_data = {
                    'game_id': str(get_game.game_id),
                    'player1': get_game.player1,
                    'player2': get_game.player2,
                    'player1_score': get_game.player1_score,
                    'player2_score': get_game.player2_score,
                    'winner': get_game.winner,
                    'state': get_game.state,
                    'type': get_game.type,
                    'date': get_game.date.strftime('%Y-%m-%d'),
                    }
                    current_match_history[str(get_game.game_id)] = new_game_data
                except Exception as e:
                    print("except", e)
                user_profile.match_history = current_match_history
                user_profile.save()
                get_game.save()
                return Response({"success": True, "winner": 1 , "type": get_game.type})
            else:
                user.profile.losses += 1
                user.profile.is_gaming = False
                try:
                    new_game_data = {
                    'game_id': str(get_game.game_id),
                    'player1': get_game.player1,
                    'player2': get_game.player2,
                    'player1_score': get_game.player1_score,
                    'player2_score': get_game.player2_score,
                    'winner': get_game.winner,
                    'state': get_game.state,
                    'type': get_game.type,
                    'date': get_game.date.strftime('%Y-%m-%d'),
                    }
                    current_match_history[str(get_game.game_id)] = new_game_data
                except Exception as e:
                    print("except", e)
                user_profile.match_history = current_match_history
                user_profile.save()
                return Response({"success": True, "lose": 1, "type": get_game.type})
        elif (get_game.player1_score and get_game.player2_score):
            return Response({"success": False})
    except:
        print("burdayım")
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
                return Response({"success": True, "playerpass": user.profile.id, "game_id": users_games.game_id, "game_state": users_games.state, "match": False})
            elif (len(users_games.waitlist) == 2 and users_games.state != 2): 
                user_player1 = User.objects.get(username=users_games.waitlist[0])
                user_player2 = User.objects.get(username=users_games.waitlist[1])

                print("hey")
                print("game_type", users_games.type)
                if (users_games.type == 0):
                    
                    url = "http://pongapi.ftpong.duckdns.org/api/new_game"
                    
                    mydata = {
                        'gameid': str(users_games.game_id),
                        'password': '4242',
                        'password_p1': str(user_player1.id),
                        'password_p2': str(user_player2.id),
                        'private': True,
                    }
                    print('mydata:', mydata)

                    try:
                        game_response = requests.post(url, json=mydata)
                    except requests.exceptions.RequestException as e:
                        print('Hata:', e)
                    print("game response", game_response)
                    if game_response.status_code == 201:
                        users_games.type = 3
                        user.profile.is_gaming = True
                        users_games.save()
                        return Response({
                            "success": True,
                            "game_pass": '4242',
                            "player": (int(user.profile.id != user_player1.id) + 1),
                            "player_pass": user.profile.id,
                            "game_id": str(users_games.game_id),
                            "game_state": users_games.state,
                            "match": True,
                        })
                    elif game_response.status_code == 409:
                        return Response({"success": False, "response": 409})
                    elif game_response.status_code == 503:
                        print(game_response.text)
                        print("5000000000333")
                        return Response({"success": False, "response": 503})
                elif (users_games.type == 3):
                    print('elif')
                    users_games.type = 5
                    users_games.state = 1
                    user.profile.is_gaming = True
                    users_games.save()
                    return Response({
                        "success": True,
                        "game_pass": '4242',
                        "player": (int(user.profile.id != user_player1.id) + 1),
                        "player_pass": user.profile.id,
                        "game_id": str(users_games.game_id),
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


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def being_tournament_match(request):
    try:
        user = request.user
        player1 = User.objects.get(username=request.data["user1"])
        player2 = User.objects.get(username=request.data["user2"])

        all_games = Game.objects.all()
        users_games = None

        if (player2.username == user.username):
            for game in all_games:
                if user.username in game.player2 and game.state == 1 and game.type == 4:
                    users_games = game
                    break
            else:
                users = {"username": request.data["user1"], "username": request.data["user2"]}
                return Response({"again": True, "users": users, "tournament_id": request.data["tournament_id"]})
            if users_games is not None :
                if (users_games.player2 == user.username and users_games.player1 == player1.username):
                    users_games.state = 2
                    users_games.save()
                    return Response({
                            "success": True,
                            "game_pass": '4243',
                            "player": 2,
                            "player_pass": player2.id,
                            "game_id": str(users_games.game_id),
                            "game_state": users_games.state,
                            "match": True,
                        })
                else:
                    users = {"username": request.data["user1"], "username": request.data["user2"]}
                    return Response({ "success": True, "again": True, "users": users, "tournament_id": request.data["tournament_id"]})
        else:
            for game in all_games:
                if user.username in game.player1 and game.state == 1 and game.type == 4:
                    print("BEİNG TOURNAMENT MATCH FOR STARTED GAME wiht player1", game.player1)
                    users_games = game
                    users_games.save()
                    return Response({
                            "success": True,
                            "game_pass": '4243',
                            "player": 2,
                            "player_pass": player1.id,
                            "game_id": str(users_games.game_id),
                            "game_state": users_games.state,
                            "match": True,
                        })
            new_game = Game.objects.create(player1 = user.username)
            new_game.player1 = player1.username
            new_game.player2 = player2.username
            new_game.type = 4
            new_game.state = 1
            new_game.save()
            url = "http://pongapi.ftpong.duckdns.org/api/new_game"
            mydata = {
                'gameid': str(new_game.game_id),
                'password': '4243',
                'password_p1': str(player1.id),
                'password_p2': str(player2.id),
                'private': True,
            }
            try:
                game_response = requests.post(url, json=mydata)
            except requests.exceptions.RequestException as e:
                print('Hata:', e)
            if game_response.status_code == 201:
                print("201 RETURN")
                return Response({
                    "success": True,
                    "game_pass": '4243',
                    "player": 1,
                    "player_pass": player1.id,
                    "game_id": str(new_game.game_id),
                    "game_state": new_game.state,
                    "match": True,
                })
            elif game_response.status_code == 409:
                """ İBO TARAFINDAN GELEN HATA """
                return Response({"success": False, "response": 409})
            elif game_response.status_code == 503:
                """ SERVER FULL ERROR İBO TARAFINDAN GELİR """
                return Response({"success": False, "response": 503})
            else:
                users = {"username": request.data["user1"], "username": request.data["user2"]}
                return Response({"success": True, "again":True, "users": users, "tournament_id": request.data["tournament_id"]})   
    except:
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


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_head_tail(request):
    try:
        game = Game.objects.get(game_id=request.data["game_id"])
        user = request.user
        if (game.state == 4 or game.state == 5):
            match_history = user.profile.match_history
            if (game.player1 == request.user.username and game.player2_score != '' and game.player2_score != None):
                new_game_data_p1 = {
                    'game_id': str(game.game_id),
                    'player1': game.player1,
                    'player2': game.player2,
                    'player1_score': game.player1_score,
                    'player2_score': game.player2_score,
                    'state': game.state,
                    'type': game.type,
                    'date': game.date.strftime('%Y-%m-%d'),
                }
                if (game.player1_score >= game.player2_score):
                    game.winner = user.profile.id
                    new_game_data_p1['winner'] = game.player1
                    match_history[str(game.game_id)] = new_game_data_p1
                    user.profile.save()
                    game.save()
                    return Response({"success": True, "winner": 1})
                else:
                    new_game_data_p1['winner'] = game.player2
                    match_history[str(game.game_id)] = new_game_data_p1
                    user.profile.save()
                    return Response({"success": True,  "lose": 1})
            elif (game.player2 == request.user.username and game.player1_score != '' and game.player1_score != None):
                new_game_data_p2 = {
                    'game_id': str(game.game_id),
                    'player1': game.player1,
                    'player2': game.player2,
                    'player1_score': game.player1_score,
                    'player2_score': game.player2_score,
                    'state': game.state,
                    'type': game.type,
                    'date': game.date.strftime('%Y-%m-%d'),
                }
                if (game.player2_score >= game.player1_score):
                    game.winner = user.profile.id
                    new_game_data_p2['winner'] = game.player2
                    match_history[str(game.game_id)] = new_game_data_p2
                    game.save()
                    user.profile.save()
                    return Response({"success": True, "winner": 1})
                else:
                    new_game_data_p2['winner'] = game.player1
                    match_history[str(game.game_id)] = new_game_data_p2
                    user.profile.save()
                    return Response({"success": True, "lose": 1})
            else:
                return Response({"success": True, "again": 1})
        else:
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
            return Response({"success": True, "notset": 2})
        elif (game.state == 5 and  game.player1 == request.user.username): #tail_score
            game.player1_score = tailclickcount
            game.save()
            return Response({"success": True, "notset": 2})
        elif (game.state == 4 and game.player2 == request.user.username):
            game.player2_score = headclickcount
            game.save()
            return Response({"success": True, "notset": 2})
        elif (game.state == 5 and game.player2 == request.user.username):
            game.player2_score = tailclickcount
            game.save()
            return Response({"success": True, "notset": 2})
    except:
        print("EXCEPT")
        return Response({"success": False})
