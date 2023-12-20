from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  avatar = models.ImageField(upload_to='avatars/', blank=False, default="avatars/default.jpg")
  total_played = models.IntegerField(default=0)
  wins = models.IntegerField(default=0)
  losses = models.IntegerField(default=0)
  friends = JSONField(default=list)
  lan = models.CharField(max_length=2, default="tr")
  is_online = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()

class Game(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  player1_id = models.IntegerField(default=0)
  player2_id = models.IntegerField(default=0)
  player1_score = models.IntegerField(default=0)
  player2_score = models.IntegerField(default=0)
  winner_id = models.IntegerField(default=0)

class Tournament(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  players = JSONField(default=list)
  winner1_id = models.IntegerField(default=0)
  winner2_id = models.IntegerField(default=0)
  waitlist = JSONField(default=list)
