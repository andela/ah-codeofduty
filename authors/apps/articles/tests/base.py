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
        # define constant urls used throughout tests
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

        self.HIGHLIGHT = '/api/articles/test-title/highlight/'
        self.HIGHLIGHT_2 = '/api/articles/test-title1/highlight/'
        self.HIGHLIGHT_ID = '/api/articles/test-title/highlight/{}/'
        self.HIGHLIGHT_ID_2 = '/api/articles/test-title1/highlight/{}/'

        self.LIKE_COMMENT = '/api/articles/{}/comment/{}/like/'
        self.DISLIKE_COMMENT = '/api/articles/{}/comment/{}/dislike/'
        self.ARTICLE_LIKES = '/api/articles/{}/like/'

        self.likes = {"likes": True}
        self.dislikes = {"likes": False}

        self.client = APIClient()

        # define user data for signup
        test_user = {
            "email": "njery.ngigi@gmail.com",
            "username": "test_user",
            "password": "test1234"
            }

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

        # define article data for create an article
        self.test_article_data = {
            "title": "test title",
            "body": "This is me testing. This line should be long enough to pass as a story.",
            "description": "testing",
            "time_to_read": 1,
            "tags": ["TDD"]
        }

        # define highlight data
        self.highlight_data = {
            "index_start": 1,
            "index_stop": 10,
            "comment": "goodie"
        }
        self.out_of_index_highlight_data = {
            "index_start": 100,
            "index_stop": 200,
            "comment": "goodie"
        }

        # signup and login 2 test users (author and non-article-author) to obtain 2 tokens for tesing
        self.test_comment_data = {
            "body": "this is a sample comment"
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

        # create 2 articles
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

    def create_comment(self, token, slug, test_comment_data):
        """ Method to create an article then comment"""
        self.client.post(self.ARTICLES, self.test_article_data,
                         HTTP_AUTHORIZATION=self.token, format='json')
        return self.client.post('/api/articles/test-title12/comment/', self.test_comment_data,
                                HTTP_AUTHORIZATION=self.token, format='json')
