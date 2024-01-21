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
  path('updateavatar/', update_avatar, name='updateavatar'),
  path('getavatar/', get_avatar, name='getavatar'),

  path('createTournament/', create_tournament, name='createTournament'),
  path('inviteTournament/', invite_tournament, name='inviteTournament'),
  path('joinTournament/', join_tournament, name='joinTournament'),
  path('tournament_table/', tournament_table, name='tournamentTable'),
  path('startTournament/', start_tournament, name='startTournament'),


  path('matching/', matching, name='matching'),
  path('headtail/', head_tail, name='headtail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)