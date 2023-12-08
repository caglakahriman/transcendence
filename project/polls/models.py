from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class Profile(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile', default=None)
    avatar = models.ImageField(default="default.jpeg", upload_to="media")


