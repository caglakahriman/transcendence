from django.urls import path
from api.views import *
from django.urls import path, include

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('userlist/', userlist),
    path('friendslist/', friendslist),
    path('addfriend/', addfriend),
    path('removefriend/', removefriend),
    path('updateavatar/', updateavatar),
    path('updatelang/', updatelang),
    path('updatename/', updatename),
    path('updatestats/', updatestats),
    path('getuserstats/', getuserstats),
    path('getuser/', getuser),
]