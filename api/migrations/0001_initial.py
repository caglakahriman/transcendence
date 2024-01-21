# Generated by Django 4.2.7 on 2024-01-21 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type', models.IntegerField(default=0)),
                ('player1', models.CharField(max_length=30)),
                ('player2', models.CharField(max_length=30)),
                ('player1_score', models.IntegerField(default=0)),
                ('player2_score', models.IntegerField(default=0)),
                ('waitlist', models.JSONField(default=list)),
                ('winner', models.IntegerField(default=0)),
                ('state', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('tournament_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('creator', models.CharField(max_length=30)),
                ('final_players', models.JSONField(default=list)),
                ('winner1', models.CharField(max_length=30)),
                ('winner2', models.CharField(max_length=30)),
                ('overall_winner', models.CharField(max_length=30)),
                ('waitlist', models.JSONField(default=list)),
                ('invitelist', models.JSONField(default=list)),
                ('state', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_history', models.JSONField(default=dict)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('friends', models.JSONField(default=list)),
                ('lan', models.CharField(default='tr', max_length=2)),
                ('is_online', models.BooleanField(default=True)),
                ('ready_to_play', models.BooleanField(default=False)),
                ('is_gaming', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
