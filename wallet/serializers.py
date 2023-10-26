from rest_framework import serializers
from wallet.models import Wallet, Transaction


class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('transaction_number', 'amount')
        extra_kwargs = {'amount': {'required': True}}

    # def validate(self, attrs):
    #     transaction_number = attrs['transaction_number']
    #     if Transaction.objects.filter(transaction_number=transaction_number).exists():
    #         raise serializers.ValidationError({'transaction_number': 'Transaction number is NOT valid'})
    #
    #     return attrs

    def create(self, validated_data):
        transaction_number = validated_data['transaction_number']
        amount = validated_data['amount']
        request = self.context.get('request', None)
        user = request.user
        wallet = user.seller.wallet

        transaction = wallet.deposit(amount, transaction_number)
        return transaction
