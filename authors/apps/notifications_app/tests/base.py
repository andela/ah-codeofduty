"""
Notifications configurations Module
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
        self.FAVOURITE = '/api/articles/{}/favorite'
        self.FOLLOW = '/api/profiles/{}/follow'
        self.COMMENT= '/api/articles/{}/comment/'
        self.ALL_NOTIFICATIONS ='/api/notifications/'
        self.MARK_AS_READ ='/api/notifications/read_notification/{}/'
        self.ALL_READ = '/api/notifications/read/'
        self.ALL_UNREAD = '/api/notifications/unread/'
        self.SUBSCRIPTION = '/api/notifications/subscription/'
        self.EMAIL_SUBSCRIPTION = '/api/notifications/subscription/{}/'

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

        self.test_article_datas = {
	        "title": "article titles",
	        "body": "Article body",
	        "description": "Article description",
	        "time_to_read": 3,
	        "tags": ["OOP"]
        }

        self.test_article_data2 = {
	        "title": "another article titles",
	        "body": "Article body",
	        "description": "Article description",
	        "time_to_read": 3,
	        "tags": ["OOP"]
        }

        self.test_commnet = {"body": "sample comment"}

        # signup the first user (article author)
        self.client.post(self.SIGN_UP_URL, self.test_user, format="json")
        response = self.client.post(self.SIGN_IN_URL, self.test_user, format="json")
        self.token = "bearer " + json.loads(response.content)["user"]["token"]

        # signup the second user 
        #   a user who can comment of favourite author's articles
        #   the user can also follow an author and get notified of 
        #   author's publications
        self.client.post(self.SIGN_UP_URL, self.test_non_author_user, format="json")
        response1 = self.client.post(self.SIGN_IN_URL, self.test_non_author_user, format="json")
        self.non_user_token = "bearer " + json.loads(response1.content)["user"]["token"]

        self.client.post(self.SIGN_UP_URL, self.test_another_non_author_user, format="json")
        response2 = self.client.post(self.SIGN_IN_URL, self.test_another_non_author_user, format="json")
        self.another_non_user_token = "bearer " + json.loads(response2.content)["user"]["token"]

        # test_non_author_user follows test_user
        self.client.put(self.FOLLOW.format('maxgit'), self.test_user['username'], HTTP_AUTHORIZATION=self.non_user_token, format="json")

        # test_user creates an article
        self.client.post(self.ARTICLES, self.test_article_datas, HTTP_AUTHORIZATION=self.token, format="json")

        # test_non_author_user creates an article
        self.client.post(self.ARTICLES, self.test_article_data2, HTTP_AUTHORIZATION=self.non_user_token, format="json")

        # test_another_non_author_user favourites test_user's article
        self.client.post(self.FAVOURITE.format("article-titles"), HTTP_AUTHORIZATION=self.non_user_token, format="json")

        # test_user favourites test_non_author_user's article
        self.client.post(self.FAVOURITE.format("another-article-titles"), HTTP_AUTHORIZATION=self.token, format="json")

        # test_another_non_author_user comments on test_user article
        self.client.post(self.COMMENT.format("article-titles"), self.test_commnet, HTTP_AUTHORIZATION=self.another_non_user_token, format="json")

        # test_another_non_author_user comments on test_non_author_user article
        self.client.post(self.COMMENT.format("another-article-titles"), self.test_commnet, HTTP_AUTHORIZATION=self.another_non_user_token, format="json")

        # test_user follows test_non_author_user
        self.client.put(self.FOLLOW.format('gitmax'), self.test_non_author_user['username'], HTTP_AUTHORIZATION=self.token, format="json")

        # test_non_author_user creates an article
        self.client.post(self.ARTICLES, self.test_article_datas, HTTP_AUTHORIZATION=self.non_user_token, format="json")
