from django.db.models import Sum
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from account.models import User
from wallet.models import Wallet, TopUpLog, Transaction


class TestWalletApp(APITestCase):

    def setUp(self) -> None:
        self.user_1_username = 'username1'
        self.user_1_password = 'qwer1470'
        self.user_2_username = 'username2'
        self.user_2_password = 'qwer1470'

        self.user_1 = User.objects.create(username=self.user_1_username)
        self.user_1.set_password(self.user_1_password)
        self.user_1.save()

        self.user_2 = User.objects.create(username=self.user_2_username)
        self.user_2.set_password(self.user_2_password)
        self.user_2.save()

        self.token_obtain_pair_url = reverse('token_obtain_pair')
        self.user_1_token_obtain_pair_data = {
            'username': self.user_1_username,
            'password': self.user_1_password
        }
        self.user_1_token_obtain_pair_response = self.client.post(self.token_obtain_pair_url,
                                                                  data=self.user_1_token_obtain_pair_data)
        self.user_1_access_token = self.user_1_token_obtain_pair_response.data['access']

        self.token_obtain_pair_url = reverse('token_obtain_pair')
        self.user_2_token_obtain_pair_data = {
            'username': self.user_2_username,
            'password': self.user_2_password
        }
        self.user_2_token_obtain_pair_response = self.client.post(self.token_obtain_pair_url,
                                                                  data=self.user_2_token_obtain_pair_data)
        self.user_2_access_token = self.user_2_token_obtain_pair_response.data['access']

        self.user_1_request_header = {
            'Authorization': f'Bearer {self.user_1_access_token}'
        }

        self.user_2_request_header = {
            'Authorization': f'Bearer {self.user_2_access_token}'
        }

        self.deposit_url = reverse('deposit')
        self.top_up_url = reverse('top_up')

    def test_transaction_and_top_up(self):
        self.assertEqual(self.user_1.seller.wallet.balance, 0)
        self.assertEqual(self.user_2.seller.wallet.balance, 0)

        data = {'transaction_number': 1, 'amount': 1000}
        transaction_1_response = self.client.post(self.deposit_url, headers=self.user_1_request_header, data=data)

        self.assertEqual(transaction_1_response.status_code, status.HTTP_201_CREATED)
        user_1_transactions = Transaction.objects.filter(wallet__seller__user=self.user_1)

        self.assertEqual(len(user_1_transactions), 1)
        self.assertEqual(user_1_transactions[0].amount, 1000)
        self.assertEqual(user_1_transactions[0].running_balance, 1000)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 1000)

        data = {'transaction_number': 1, 'amount': 1900}
        transaction_2_response = self.client.post(self.deposit_url, headers=self.user_1_request_header, data=data)
        self.assertEqual(transaction_2_response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Wallet.objects.get(seller__user__username=self.user_1_username).balance, 1000)
        self.assertEqual(len(Transaction.objects.filter(wallet__seller__user=self.user_1)), 1)

        data = {'transaction_number': 2, 'amount': 1900}
        self.client.post(self.deposit_url, headers=self.user_1_request_header, data=data)

        self.assertEqual(len(Transaction.objects.filter(wallet__seller__user=self.user_1)), 2)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 2900)

        data = {'transaction_number': 1, 'amount': 500}
        transaction_4_response = self.client.post(self.deposit_url, headers=self.user_2_request_header, data=data)

        self.assertEqual(transaction_4_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.filter(wallet__seller__user=self.user_2)), 0)

        data = {'transaction_number': 3, 'amount': 500}
        transaction_5_response = self.client.post(self.deposit_url, headers=self.user_2_request_header, data=data)
        self.assertEqual(transaction_5_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Transaction.objects.filter(wallet__seller__user=self.user_2)), 1)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_2).balance, 500)

        data = {'phone_number': '08195556633', 'amount': 10}
        top_up_1_response = self.client.post(self.top_up_url, headers=self.user_1_request_header, data=data)
        self.assertEqual(top_up_1_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 2900)
        self.assertEqual(len(TopUpLog.objects.filter(wallet__seller__user=self.user_1)), 0)

        data = {'phone_number': '09195556633', 'amount': 10}
        top_up_2_response = self.client.post(self.top_up_url, headers=self.user_1_request_header, data=data)
        self.assertEqual(top_up_2_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 2890)
        self.assertEqual(len(TopUpLog.objects.filter(wallet__seller__user=self.user_1)), 1)
        self.assertEqual(TopUpLog.objects.get(wallet__seller__user=self.user_1).amount, 10)

        data = {'phone_number': '09195556633', 'amount': 2900}
        top_up_3_response = self.client.post(self.top_up_url, headers=self.user_1_request_header, data=data)
        self.assertEqual(top_up_3_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 2890)
        self.assertEqual(len(TopUpLog.objects.filter(wallet__seller__user=self.user_1)), 1)

        data = {'phone_number': '09195556633', 'amount': 2890}
        top_up_4_response = self.client.post(self.top_up_url, headers=self.user_1_request_header, data=data)
        self.assertEqual(top_up_4_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wallet.objects.get(seller__user=self.user_1).balance, 0)
        self.assertEqual(len(TopUpLog.objects.filter(wallet__seller__user=self.user_1)), 2)

        total_top_ups = TopUpLog.objects.filter(wallet__seller__user=self.user_1).aggregate(amount=Sum('amount'))[
            'amount']
        self.assertEqual(total_top_ups, 2900)
