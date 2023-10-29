from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from account.models import User, Seller
from wallet.models import Wallet


class TestAccountApp(APITestCase):

    def setUp(self) -> None:
        self.username = 'username'
        self.password = 'qwer1470'
        self.user_data = {
            'username': self.username,
            'password': self.password,
        }

        self.signup_payload = self.user_data
        self.signup_payload['repeat_password'] = self.password
        self.signup_url = reverse('signup')
        self.signup_data = self.signup_payload
        self.signup_response = self.client.post(self.signup_url, data=self.signup_data)

        self.login_payload = self.user_data
        self.token_obtain_pair_url = reverse('token_obtain_pair')
        self.token_obtain_pair_data = self.login_payload
        self.token_obtain_pair_response = self.client.post(self.token_obtain_pair_url, data=self.token_obtain_pair_data)

        self.token_refresh_url = reverse('token_refresh')
        self.token_refresh_data = {
            'refresh': self.token_obtain_pair_response.data['refresh']
        }
        self.refresh_token_response = self.client.post(self.token_refresh_url, data=self.token_refresh_data)

    def test_signup(self):
        self.assertEqual(self.signup_response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        self.assertEqual(self.token_obtain_pair_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh_token_response.status_code, status.HTTP_200_OK)

    def test_signals(self):
        user_exists = User.objects.filter(username=self.username).exists()
        seller_exists = Seller.objects.filter(user__username=self.username).exists()
        wallet_exists = Wallet.objects.filter(seller__user__username=self.username).exists()

        self.assertTrue(user_exists)
        self.assertTrue(seller_exists)
        self.assertTrue(wallet_exists)
