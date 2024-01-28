from django.urls import path
from api.views import *
from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('register/', register_user, name='register'),
  path('login/', login_user, name='login'),
  path('logout/', logout_user, name='logout'),
  path('auth/', obtain_auth_token, name='auth'),
  path('authtest/', authenticated_test, name='authtest'),


  path('friendslist/', friendslist, name='friendslist'),
  path('addfriend/', addfriend, name='addfriend'),
  path('removefriend/', removefriend, name='removefriend'),

  path('search/', search, name='search'),
  path('getprofile/', get_profile, name='getprofile'),
  path('getmyprofile/', get_myprofile, name='getmyprofile'),
  path('update_avatar/', update_avatar, name='updateavatar'),
  path('getavatar/', get_avatar, name='getavatar'),
  path('update_profile/', update_profile, name='updateprofile'),

  path('createTournament/', create_tournament, name='createTournament'),
  path('inviteTournament/', invite_tournament, name='inviteTournament'),
  path('joinTournament/', join_tournament, name='joinTournament'),
  path('tournament_table/', tournament_table, name='tournamentTable'),
  path('startTournament/', start_tournament, name='startTournament'),
  path('being-tournament-match/', being_tournament_match, name='beingTournamentMatch'),
  path('first-match/', first_match, name='firstMatch'),
  path('tournament-winner/', tournament_winner, name='tournamentWinner'),
  path('game-info-back/', game_info_back, name='game_info_back'),
  path('matching/', matching, name='matching'),
  path('clean-tournament/', clean_tournament, name='cleanTournament'),

  path('head-tail/', head_tail, name='head-tail'),
  path('head-and-tail-race/', head_tail_race, name='head_tail_race'),
  path('check-head-tail/', check_head_tail, name='check_head_tail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)