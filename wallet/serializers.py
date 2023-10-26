from rest_framework import serializers
from wallet.models import Wallet, Transaction
from django.db.utils import IntegrityError


class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('transaction_number', 'amount')
        extra_kwargs = {'amount': {'required': True}}

    def create(self, validated_data):
        transaction_number = validated_data['transaction_number']
        amount = validated_data['amount']
        request = self.context.get('request', None)
        user = request.user
        wallet = user.seller.wallet

        try:
            transaction = wallet.deposit(amount, transaction_number)
        except IntegrityError:
            raise serializers.ValidationError({"transaction_number": "Invalid transaction number"})

        return transaction
