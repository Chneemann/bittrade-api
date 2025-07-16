from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from wallets.models import Wallet
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance)

@receiver(post_delete, sender=Wallet)
def recreate_wallet_after_delete(sender, instance, **kwargs):
    user = instance.user
    if not Wallet.objects.filter(user=user).exists():
        Wallet.objects.create(user=user)