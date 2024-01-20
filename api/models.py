from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  avatar = models.ImageField(upload_to='avatars/', blank=False, default="avatars/default.jpg")
  total_played = models.IntegerField(default=0)
  wins = models.IntegerField(default=0)
  losses = models.IntegerField(default=0)
  friends = JSONField(default=list)
  lan = models.CharField(max_length=2, default="tr")
  is_online = models.BooleanField(default=True)
  is_gaming = models.BooleanField(default=False) #if user accepts an invite or creates a game, this variable should be True.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()


class Game(models.Model): #oyun game id
  date = models.DateTimeField(auto_now_add=True)
  type = models.IntegerField(default=0) #0: ping-pong, 1: head-and-tails
  player1_token = models.IntegerField(default=0)
  player2_token = models.IntegerField(default=0) 
  player1_score = models.IntegerField(default=0)
  player2_score = models.IntegerField(default=0)
  winner_token = models.IntegerField(default=0)
  state = models.IntegerField(default=0) #0: not started, 1: started, 2: finished

class Tournament(models.Model):
  tournament_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  date = models.DateTimeField(auto_now_add=True)
  creator = models.CharField(max_length=30)
  final_players = JSONField(default=list)
  winner1_token = models.IntegerField(default=0)
  winner2_token = models.IntegerField(default=0)
  overall_winner_token = models.IntegerField(default=0)
  waitlist = JSONField(default=list)
  invitelist = JSONField(default=list)
  state = models.IntegerField(default=0) #0: not started, 1: started, 2: finished
