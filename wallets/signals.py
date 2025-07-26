from django.db.models.signals import post_save
from django.dispatch import receiver
from wallets.models import Wallet
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance)