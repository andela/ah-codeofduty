"""test configurations"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.views import status
from django.urls import reverse


class BaseTest(TestCase):
    """
      Test user views
      :param: TestCase: Testing class initializer
    """

    def setUp(self):
        """Define the test client"""
        self.SIGN_IN_URL = '/api/users/login/'
        self.SIGN_UP_URL = '/api/users/'
        self.USER_URL = '/api/user/'
        self.FORGOT_URL = '/api/users/forgot-password/'

        # TODO: reset-password
        # self.RESET_URL = '/api/users/reset-password/{}'.format(self.reset_token)

        test_user = {"email": "njery.ngigi@gmail.com",
                     "username": "test_user",
                     "password": "test1234"}

        self.client.post(self.SIGN_UP_URL, test_user, format="json")

        self.client = APIClient()
        self.user_data = {
                'email': 'zawi@gmail.com',
                'username': 'zawi',
                'password': 'password1234'
            }

        self.user_email_exists = {
                'email': 'zawi@gmail.com',
                'username': 'zawadi',
                'password': 'password1234'
            }

        self.user_username_exists = {
                'email': 'zawadi@gmail.com',
                'username': 'zawi',
                'password': 'password1234'
            }

        self.user_missing_fields = {
                'email': '',
                'username': '',
                'password': ''
            }

        self.user_missing_username_parameter = {
                'email': 'zawi@gmail.com',
                'username': '',
                'password': 'password1234'
            }

        self.user_missing_email_parameter =  {
                'email': '',
                'username': 'zawi',
                'password': 'password1234'
            }


        self.user_inputs_short_password = {
                'email': 'zawi@gmail.com',
                'username': 'zawi',
                'password': 'pass'
            }

        self.user_inputs_invalid_email = {
                'email': 'zawi.com',
                'username': 'zawi',
                'password': 'password1234'
            }

        self.user_wrong_password= {
                'email': 'zawi@gmail.com',
                'username': 'zawi',
                'password': 'wrong_password'
            }

        self.user_does_not_exist = {
                'email': 'zawizawi@gmail.com',
                'username': 'zawadi',
                'password': 'password1234'
            }

        self.missing_password = {
                'email': 'mathias@gmail.com',
                'username': 'mathias',
                'password': ''
            }
  
    def register_user(self):
        """User registration"""

        return self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")

    def login_user(self):
        """User login"""

        return self.client.post(
            self.SIGN_IN_URL,
            self.user_data,
            format="json")
