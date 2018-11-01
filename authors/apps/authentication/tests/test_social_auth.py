from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse as api_reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SocialAuthSignupSignin(APITestCase):
    def setUp(self):
        self.access_token = 'EAAe6UMnIZBRoBAG9GEsj3TwlzejSsWf4s2r0RmG8BMpwqJxx3dwCWAremGJHEQHiMJa2ro2Nk68zeqf7Pwy9gtTrqBdHODT5XlYlL2mpfNc3pBamkHoclJZCSty3WZCGh0qvP6kZCO5nse54tbtfh0YACsU3hdGk8XjyrRZBxIcA2Cr5C9nOvRPvnDZA2DURoHuTrvuGda7BAJPXKTfrZCPJ2bPUAqnW836eNWpldIzJLMA8GrBzJLN'
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
