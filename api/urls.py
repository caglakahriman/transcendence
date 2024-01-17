from django.urls import path
from api.views import *
from django.urls import path, include

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('userlist/', userlist),

    # FRIENDS #################################
    path('friendslist/', friendslist),
    path('addfriend/', addfriend),
    path('removefriend/', removefriend),
    ###########################################

    path('updateavatar/', updateavatar),
    path('updatelang/', updatelang),
    path('updatename/', updatename),

    path('updatestats/', updatestats),
    path('getuserstats/', getuserstats),
    
    # PROFILE #################################
    path('updateprofile/', updateprofile),
    path('getprofile/', get_profile),
    ###########################################
    
    # TOURNAMENTS #############################
    path('createTournament/', createTournament),
    path('inviteTournament/', inviteTournament),
    path('acceptTournament/', inviteTournament),
    ###########################################
]