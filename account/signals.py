from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import Seller
from wallet.models import Wallet


@receiver(post_save, sender=Seller)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(Seller=instance)
