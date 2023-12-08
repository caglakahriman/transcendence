from django.urls import path, include
from rest_framework import routers
from polls import views
from django.conf.urls.static import static
from django.conf import settings

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserView, 'user')

urlpatterns = [
    path('<str:user_name>/', views.searchUser, name='user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)