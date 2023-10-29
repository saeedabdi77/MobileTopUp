import time

from django.utils.translation import gettext as _
from django.core.validators import RegexValidator
from django.db import models
from account.models import Seller
from django.db import transaction
from utils.top_up_tools import top_up_phone_number


class Wallet(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)

    @transaction.atomic
    def deposit(self, amount, transaction_number):
        Wallet.objects.select_for_update().get(id=self.id)

        balance = Wallet.objects.get(id=self.id).balance + amount

        transaction = self.transactions.create(
            transaction_number=transaction_number,
            amount=amount,
            running_balance=balance,
        )

        self.balance = balance
        self.save()

        return transaction

    @transaction.atomic
    def top_up(self, amount, phone_number):
        Wallet.objects.select_for_update().get(id=self.id)

        balance = Wallet.objects.get(id=self.id).balance
        if amount > balance:
            raise ValueError('Not enough balance')

        top_up_phone_number(phone_number, amount)
        top_up = TopUpLog.create_log(self, phone_number, amount)
        self.balance -= amount
        self.save()

        return top_up

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
    phone_regex = RegexValidator(regex=r'(09)[0-9]{9}$',
                                 message=_('invalid phone number'))
    phone_number = models.CharField(max_length=11, validators=[phone_regex])
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_log(wallet, phone_number, amount):
        log = TopUpLog.objects.create(wallet=wallet,
                                      phone_number=phone_number,
                                      amount=amount)
        return log
