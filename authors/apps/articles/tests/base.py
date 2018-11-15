"""test configurations"""
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
        self.ARTICLE = '/api/articles/{}/'
        self.TESTARTICLE = '/api/articles/test-title/'

        self.CREATE_A_COMMENT = '/api/articles/{}/comment/'
        self.FETCH_ALL_COMMENTS = '/api/articles/{}/comment/'

        self.CREATE_A_REPLY = '/api/articles/{}/comment/{}/'
        self.FETCH_A_COMMENT = '/api/articles/{}/comment/{}/'
        self.UPDATE_A_COMMENT = '/api/articles/{}/comment/{}/'
        self.DELETE_A_COMMENT = '/api/articles/{}/comment/{}/'

        self.ARTICLE_LIKES = '/api/articles/{}/like/'

        self.likes = {"likes": True}
        self.dislikes = {"likes": False}

        self.client = APIClient()
        test_user = {
            "email": "njery.ngigi@gmail.com",
            "username": "test_user",
            "password": "test1234"}
        test_non_author_user = {
            "email": "njeringigi59@gmail.com",
            "username": "non_user",
            "password": "test1234"

        }

        self.fav_test_user = {
            "email": "njery.ngigi@gmail.com",
            "username": "test_user",
            "password": "test1234"
        }

        self.test_article_data = {
            "title": "test title",
            "body": "This is me testing",
            "description": "testing",
            "time_to_read": 1,
            "tags": ["TDD"]
        }

        self.client.post(self.SIGN_UP_URL, test_user, format="json")
        response = self.client.post(self.SIGN_IN_URL, test_user, format="json")
        self.token = "bearer " + json.loads(response.content)["user"]["token"]

        self.client.post(self.SIGN_UP_URL, test_non_author_user, format="json")
        response = self.client.post(
            self.SIGN_IN_URL, test_non_author_user, format="json")
        self.non_user_token = "bearer " + \
            json.loads(response.content)["user"]["token"]
        response2 = self.client.post(self.SIGN_IN_URL, test_non_author_user, format="json")
        self.token2 = "bearer " + json.loads(response2.content)["user"]["token"]

        self.client.post(self.ARTICLES, self.test_article_data,
                         HTTP_AUTHORIZATION=self.token, format="json")
        self.client.post(self.ARTICLES, self.test_article_data,
                         HTTP_AUTHORIZATION=self.token, format="json")

    def favorite_article(self, slug, token):
        return self.client.post(
            self.ARTICLES + slug + '/favorite',
            HTTP_AUTHORIZATION='Bearer ' + token,
            format='json'
        )

    def unfavorite_article(self, slug, token):
        return self.client.delete(
            self.ARTICLES + slug + '/favorite',
            HTTP_AUTHORIZATION='Bearer ' + token,
            format='json'
        )

    def create_article(self, article, token):
        return self.client.post(
            self.ARTICLES,
            article,
            HTTP_AUTHORIZATION='Bearer ' + token,
            format='json'
        )
