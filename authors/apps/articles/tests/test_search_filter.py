import json
from rest_framework.views import status
from .base import BaseTest

class SearchTestCase(BaseTest):
    def test_search_article_by_title(self):
        response = self.client.post(
            self.SIGN_UP_URL,
            self.fav_test_user,
            format='json'
        )
        response = self.client.post(
            self.SIGN_IN_URL,
            self.fav_test_user,
            format='json'
        )
        token = response.data["token"]
        response = self.create_article(self.test_article_data, token)
        token = ''
        response = self.client.get('/api/search/articles/?title=title')

        self.assertEquals(status.HTTP_200_OK, response.status_code)
    
    def test_search_article_by_tag(self):
        response = self.client.post(
            self.SIGN_UP_URL,
            self.fav_test_user,
            format='json'
        )
        response = self.client.post(
            self.SIGN_IN_URL,
            self.fav_test_user,
            format='json'
        )
        token = response.data["token"]
        response = self.create_article(self.test_article_data, token)
        response = self.client.get('/api/search/articles/?tag=tdd')

        self.assertEquals(status.HTTP_200_OK, response.status_code)
    
    def test_search_article_by_author(self):
        response = self.client.post(
            self.SIGN_UP_URL,
            self.fav_test_user,
            format='json'
        )
        response = self.client.post(
            self.SIGN_IN_URL,
            self.fav_test_user,
            format='json'
        )
        token = response.data["token"]
        response = self.create_article(self.test_article_data, token)
        response = self.client.get('/api/search/articles/?author=test_user')

        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_search_article_by_author_not_found(self):
        response = self.client.post(
            self.SIGN_UP_URL,
            self.fav_test_user,
            format='json'
        )
        response = self.client.post(
            self.SIGN_IN_URL,
            self.fav_test_user,
            format='json'
        )
        token = response.data["token"]
        response = self.create_article(self.test_article_data, token)
        response = self.client.get('/api/search/articles/?author=thanos')

        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_search_article_by_tag_not_found(self):
        response = self.client.post(
            self.SIGN_UP_URL,
            self.fav_test_user,
            format='json'
        )
        response = self.client.post(
            self.SIGN_IN_URL,
            self.fav_test_user,
            format='json'
        )
        token = response.data["token"]
        response = self.create_article(self.test_article_data, token)
        response = self.client.get('/api/search/articles/?tag=lose')

        self.assertEquals(status.HTTP_200_OK, response.status_code)
        