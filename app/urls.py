"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from rest_framework import routers
from polls import views

router = routers.DefaultRouter()
router.register(r'users', views.UserView, 'user')

urlpatterns = [
    path('', view=views.main, name="main"),
    path('login/', view=views.login, name="login"),
    path('register/', view=views.register, name="register"),
    path('logout/', view=views.logout, name="logout"),
    path('auth42/', view=views.auth42, name="auth42"),
    path('users/', view=views.users, name="users"),
    path('polls/', include("polls.urls")), #include allows referencing other URLconfs
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
