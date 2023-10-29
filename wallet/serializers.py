from rest_framework import serializers
from wallet.models import Transaction, TopUpLog
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
    

class TopUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopUpLog
        fields = ('phone_number', 'amount')
        extra_kwargs = {'amount': {'required': True}}

    def get_current_user_wallet(self):
        request = self.context.get('request', None)
        user = request.user
        wallet = user.seller.wallet

        return wallet

    def validate(self, attrs):
        wallet = self.get_current_user_wallet()
        amount = attrs['amount']

        if amount > wallet.balance:
            raise serializers.ValidationError({"amount": "Not enough balance"})
        return attrs

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        amount = validated_data['amount']
        wallet = self.get_current_user_wallet()
        try:
            top_up = wallet.top_up(amount, phone_number)
        except ValueError:
            raise serializers.ValidationError({"amount": "Not enough balance"})

        return top_up
