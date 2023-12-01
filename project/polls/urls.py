from django.urls import path, include
from rest_framework import routers
from polls import views

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserView, 'user')

urlpatterns = [
    path('<str:user_name>/', views.searchUser, name='user'),
]