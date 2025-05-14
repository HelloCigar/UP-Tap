# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=Token)
def token_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"Token created for user {instance.user.email}: {instance.key}")
        # with open(".txt", "a") as f:
        # f.write(f"{message}\n")
    