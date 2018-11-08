"""
Rate articles test module
"""

import json

from rest_framework.views import status

from .base import BaseTest


class RateArticleTestCase(BaseTest):
    """
    Rate articles tests class
    :params: BaseTest:
      the base test class
    """

    def test_rate_article(self):
        """
        test article is rated successfully
        """
        # test successful creating article
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(3, json.loads(response.content)["rating"])

    def test_author_cannot_rate_their_article(self):
        """
        test article authors cannot rate their article
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Error, you can\'t rate your own article', json.loads(response.content)['errors'][0])

    def test_non_existing_article(self):
        """
        test non-existing article
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        response = self.client.post(self.RATE.format('new-titl'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Error, Article does not exist', json.loads(response.content)['errors'][0])

    def test_rate_article_with_invalid_credentials(self):
        """
        test article rated by unauthorized user
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        self.non_user_token = ('Bearer Token')
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual('cannot decode token', json.loads(response.content)['detail'])

    def test_article_with_invalid_rating(self):
        """
        Test article rating is between 1-5
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 0}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])

        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        rating = {"rating": 6}
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Error, rating is between 1 to 5', json.loads(response.content)['errors'][0])

    def test_get_average_rating(self):
        """
        test get average rating of an article
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #rate article again
        rating["rating"] =  4
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test successful get of average rating
        response = self.client.get(self.ARTICLE.format('new-title'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, json.loads(response.content)["avaragerating"])

    def test_get_average_rating_of_non_existing_article(self):
        """
        test non-existing article cannot be rated
        """
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        rating = {"rating": 3}
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('new title', json.loads(response.content)["title"])
        #rate article
        response = self.client.post(self.RATE.format('new-title'), rating, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test successful get
        response = self.client.get(self.ARTICLE.format('new-titl'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual('This article doesn\'t exist', json.loads(response.content)['detail'])
