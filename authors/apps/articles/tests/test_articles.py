'''articles/test_articles.py'''
import json
from rest_framework.views import status
from .base import BaseTest

class ArticleTestCase(BaseTest):
    '''class testing CRUD functions for articles'''
    def test_create_article(self):
        '''test creating article'''
        # test successful creating article
        article_data = {
	        "title": "new title",
	        "body": "mama mia is never going to England1",
	        "description": "happy feet",
	        "time_to_read": 1,
	        "tags": ["math", "science"]
        }
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(article_data["title"], json.loads(response.content)["title"])
        # test missing fields
        del article_data["title"]
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["errors"]["title"][0], "This field is required.")
        # test very long title
        article_data["title"] = "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjkzxcvbnmqwertyuiopasdfghjklxcvbnmqwertyuiopasdfghjklzxcvbnm"
        response = self.client.post(self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["errors"]["title"][0], "Ensure this field has no more than 100 characters.")
        # test unlogged in user (missing authorization header)
        article_data["title"] = "new title"
        response = self.client.post(self.ARTICLES, article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content)["detail"], "Authentication credentials were not provided.")
    
    def test_get_all_articles(self):
        '''test get all articles'''
        # test successful get
        response = self.client.get(self.ARTICLES)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertGreaterEqual(len(json.loads(response.content)), 0)

    def test_get_single_article(self):
        '''test get single article'''
        # test successful get
        response = self.client.get(self.TESTARTICLE)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(self.test_article_data["title"], json.loads(response.content)["title"])

        # test non-existent article
        response = self.client.get(self.ARTICLE.format("never-the-new-one"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
        self.assertGreaterEqual(json.loads(response.content)["detail"], "This article doesn't exist")

    def test_update_article(self):
        '''test update article'''
        # test successful update
        article_data = {
	        "title": "The very newest title",
        }
        response = self.client.put(self.TESTARTICLE, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(article_data["title"], json.loads(response.content)["title"])
        # test non-author
        response = self.client.put(self.TESTARTICLE, article_data, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content)["detail"], "You do not have permission to perform this action.")
        # test non-existent article
        response = self.client.put(self.ARTICLE.format("never-the-newest-title"), article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "This article doesn't exist")

    def test_delete_article(self):
        '''test delete article'''
        # test non-author
        response = self.client.delete(self.ARTICLE.format("test-title1"), HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content)["detail"], "You do not have permission to perform this action.")
        # test successful delete
        response = self.client.delete(self.ARTICLE.format("test-title1"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)["message"], "Article test-title1 deleted successfully")
        # test non-existent article
        response = self.client.delete(self.ARTICLE.format("test-title1"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "This article doesn't exist")
