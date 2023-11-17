from django.urls import path, include
from rest_framework import routers
from polls import views

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserView, 'user')

urlpatterns = [
    path('', views.pollindex, name='pollindex'),
      # API endpoint
    # /users/ lists all users (CREATE & DELETE)
    # /users/<id> lists user with id (UPDATE & DELETE)
    path('<str:user_name>/', views.searchUser, name='user')
]