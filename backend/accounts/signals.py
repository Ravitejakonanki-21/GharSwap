from django.db.models.signals import post_save
from django.dispatch import receiver

from credits.services import grant_signup_bonus

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile_and_bonus(sender, instance, created, **kwargs):
    if not created:
        return
    display_name = instance.email.split("@")[0]
    Profile.objects.get_or_create(
        user=instance, defaults={"display_name": display_name}
    )
    grant_signup_bonus(instance)
