from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import Seller, User
from wallet.models import Wallet


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Seller.objects.create(user=instance)


@receiver(post_save, sender=Seller)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(seller=instance)
