from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user_ref=instance)
  instance.profile.save()