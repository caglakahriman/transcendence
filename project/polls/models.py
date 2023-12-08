from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  avatar = models.ImageField(upload_to='avatars/', blank=True, default="avatars/default.jpg")
  match_history = JSONField(default=list)