from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Game, Tournament


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', ]

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = Profile
        fields = ['user', 'avatar', 'total_played', 'wins', 'losses', 'friends', 'lan', 'nickname', 'is_online']
    
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['date', 'player1_id', 'player2_id', 'player1_score', 'player2_score', 'winner_id']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['date', 'players', 'winner1_id', 'winner2_id', 'waitlist']