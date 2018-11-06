import os
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse as api_reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SocialAuthSignupSignin(APITestCase):
    def setUp(self):
        self.access_token = os.getenv('GOOGLE_TOKEN')
        self.social_url = api_reverse('authentication:social_signin_signup')
        user_data = User(
            username='testuser',
            email='test@gmail.com',
            is_active=True
        )
        user_data.set_password('UserStrongPass@22')
        user_data.save()

    def test_empty_provider_field(self):
        """test for error code thrown when no provider name given"""
        data = {"access_token": self.access_token}
        resp = self.client.post(self.social_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_for_no_token_provided(self):
        """this method test that social authentication
        error if no provider token in the field of provider"""
        provider = 'google-oauth2'
        data = {"provider": provider}
        resp1 = self.client.post(self.social_url, data=data)
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_google_social_login(self):
        """this method test that social authentication
        error if no provider token in the field of provider"""
        provider = "google-oauth2"
        data = {"provider": provider, "access_token": self.access_token}
        resp2 = self.client.post(self.social_url, data=data)
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

    def test_twitter_social_login(self):
        """this method test that social authentication
        error if no provider token in the field of provider"""
        provider = "twitter"

        data = {"provider": provider, "access_token": os.getenv(
            'TWITTER_ACCESS_TOKEN'), "access_token_secret": os.getenv('TWITTER_TOKEN_SECRET')}
        resp2 = self.client.post(self.social_url, data=data)
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
