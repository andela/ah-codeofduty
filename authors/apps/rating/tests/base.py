"""
Rating configurations Module
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient

class BaseTest(TestCase):
    """
      Test user views
      :param: TestCase: Testing class initializer
    """

    def setUp(self):
        """Define the test client"""
        self.SIGN_IN_URL = '/api/users/login/'
        self.SIGN_UP_URL = '/api/users/'
        self.ARTICLES = '/api/articles/'
        self.ARTICLE =  '/api/articles/{}/'
        self.TESTARTICLE = '/api/articles/test-title/'
        self.RATE = '/api/articles/{}/rate/'

        self.client = APIClient()

        self.test_user = {
            "email": "maxgit@email.com",
            "username": "maxgit",
            "password": "A2wertyuio"}

        self.test_non_author_user = {
            "email": "gitmax@email.com",
            "username": "gitmax",
            "password": "A2wdfbnjiop"}

        self.test_another_non_author_user = {
            "email": "well@email.com",
            "username": "wellgit",
            "password": "A2wdfbnjiorp"}

        self.test_article_data = {
	        "title": "article title",
	        "body": "Article body",
	        "description": "Article description",
	        "time_to_read": 3,
	        "tags": ["OOP"]
        }

        self.test_rating = {"rating": 4}

        self.client.post(self.SIGN_UP_URL, self.test_user, format="json")
        response = self.client.post(self.SIGN_IN_URL, self.test_user, format="json")
        self.token = "bearer " + json.loads(response.content)["user"]["token"]

        self.client.post(self.SIGN_UP_URL, self.test_non_author_user, format="json")
        response1 = self.client.post(self.SIGN_IN_URL, self.test_non_author_user, format="json")
        self.non_user_token = "bearer " + json.loads(response1.content)["user"]["token"]

        self.client.post(self.SIGN_UP_URL, self.test_another_non_author_user, format="json")
        response2 = self.client.post(self.SIGN_IN_URL, self.test_another_non_author_user, format="json")
        self.another_non_user_token = "bearer " + json.loads(response2.content)["user"]["token"]

        self.client.post(self.ARTICLES, self.test_article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.client.post(self.ARTICLES, self.test_article_data, HTTP_AUTHORIZATION=self.token, format="json")
