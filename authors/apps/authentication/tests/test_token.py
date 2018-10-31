"""
Token related tests module
"""
import json

from rest_framework.views import status

from .base import BaseTest

class TokenTestcase(BaseTest):
    """Test tokens testcase"""


    def test_token_without_bearer(self):
        """
        test token must have a 'Bearer' prefix
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token akldjfakjdlfjs")

        get_user = self.client.get(
            self.USER_URL
        )
        self.output = json.loads(get_user.content)['user']['detail']
        self.assertEqual(get_user.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.output, 'Authentication credentials were not provided.')


    def test_token_without_string_token(self):
        """
        test token must have a token string
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer ")

        get_user = self.client.get(
            self.USER_URL
        )
        self.output = json.loads(get_user.content)['user']['detail']
        self.assertEqual(get_user.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.output, 'Invalid token header. No credentials provided.')


    def test_token_with_invalid_content(self):
        """
        test token must not have invalid content
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer kksdjkskjjds dsjkdksjd ")

        get_user = self.client.get(
            self.USER_URL
        )
        self.output = json.loads(get_user.content)['user']['detail']
        self.assertEqual(get_user.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.output, 'Invalid token header')



    def test_authenticates_user(self):
        """
        Test sucessful token generation on login
        """
        register = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        login = self.client.post(
            self.SIGN_IN_URL,
            self.user_data,
            format="json")
        token = json.loads(login.content)['user']['token']
        self.client.credentials(HTTP_AUTHORIZATION="Bearer "+token)
        self.assertIn('token', login.data)
        self.assertEqual(token, login.data['token'])


    def test_invalid_token(self):
        """
        Test secured endpoint must have a valid token
        """
        register = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json",
        )    
        login = self.client.post(
            self.SIGN_IN_URL,
            self.user_data,
            format="json")

        token = json.loads(login.content)['user']['token']

        #tamper with the token authorizarion header
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + 'token')

        #try acessing a secured endpoint
        get_user = self.client.get(
        self.USER_URL
        )

        self.assertTrue('cannot decode token', json.loads(get_user.content)['user']['detail'])
