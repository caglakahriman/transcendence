from django.urls import path
from api.views import *
from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
  path('register/', register_user, name='register'),
  path('auth/', obtain_auth_token, name='auth'),
  path('authtest/', authenticated_test, name='authtest'),
]