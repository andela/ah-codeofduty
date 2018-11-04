import json

from rest_framework.test import APIClient
from django.test import TestCase


class BaseTest(TestCase):

    def setUp(self):
        self.user_data = {
                "username": "mathias",
                "email": "mathias@gmail.com",
                "password": "mathias92"
            }

        self.login_data = {
                "email": "mathias@gmail.com",
                "password": "mathias92"
            }

        self.client = APIClient()

        self.register_response = self.client.post("/api/users/", self.user_data, format="json")
        self.login_response = self.client.post("/api/users/login/", self.login_data, format="json")
        token = json.loads(self.login_response.content)['user']['token']
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
