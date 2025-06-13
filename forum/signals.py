from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a Profile when a new User is created.

    Args:
        sender: The model class that sent the signal (User)
        instance: The actual instance being saved (User instance)
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments

    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the Profile when the User is saved.

    Args:
        sender: The model class that sent the signal (User)
        instance: The actual instance being saved (User instance)
        **kwargs: Additional keyword arguments

    """
    # Ensure the profile exists before trying to save it
    # This handles cases where a user might have been created before this signal was implemented
    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
