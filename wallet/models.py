from django.db import models
from account.models import Seller
from django.db import transaction


class Wallet(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)

    @transaction.atomic
    def deposit(self, amount, transaction_number):
        Wallet.objects.filter(id=self.id).select_for_update(nowait=False).get()

        transaction = self.transactions.create(
            transaction_number=transaction_number,
            amount=amount,
            running_balance=self.balance + amount,
        )

        self.balance += amount
        self.save()

        return transaction

    @transaction.atomic
    def top_up(self, amount, phone_number):
        if amount > self.balance:
            # raise error
            raise

        # call top up function
        TopUpLog.create_log(self, phone_number, amount)
        self.balance -= amount
        self.save()

    def __str__(self):
        username = self.seller.user.username
        return f'{username}  wallet'


class Transaction(models.Model):
    transaction_number = models.CharField(unique=True, max_length=250)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField(default=0)
    running_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class TopUpLog(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='top_up_logs')
    phone_number = models.CharField(max_length=25)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_log(wallet, phone_number, amount):
        TopUpLog.objects.create(wallet=wallet,
                                phone_numbe=phone_number,
                                amount=amount)
