from .base import BaseTest
from rest_framework.views import status


class ReportArticleTestCase(BaseTest):
    def get_token(self):
        response = self.client.post(self.SIGN_UP_URL, self.fav_test_user, format='json')
        response = self.client.post(self.SIGN_IN_URL, self.fav_test_user, format='json')
        token = response.data['token']
        return token

    def create_article(self, token, article):
        """ Method to create an article"""
        return self.client.post(self.ARTICLES, self.test_article_data,
                                HTTP_AUTHORIZATION='Bearer ' + token, format='json')

    def test_report_without_authentication(self):
        """Test if user can report an article without authentication"""
        response = self.client.put(path='/api/articles/test-title12/report')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_report_articles(self):
        """Test the reporting article successful"""
        token = self.get_token()
        article_data = {
            "title": "test title",
            "body": "This is me testing",
            "description": "testing",
            "time_to_read": 1,
            "tags": ["TDD"]
        }

        response = self.create_article(token, article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        test_report_data = {
            "body": "this is a sample report"
        }
        response = self.client.post(path='/api/articles/test-title12/report', data=test_report_data,
                                    HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_report_no_body(self):
        """Test reporting article without report body"""
        token = self.get_token()
        article_data = {
            "title": "test title",
            "body": "This is me testing",
            "description": "testing",
            "time_to_read": 1,
            "tags": ["TDD"]
        }

        response = self.create_article(token, article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        test_report_data = {
            "body": ""
        }
        response = self.client.post(path='/api/articles/test-title12/report', data=test_report_data,
                                    HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_missing_article(self):
        """Test test the reporting article successful"""
        test_report_data = {
            "body": "this is a sample report"
        }
        response = self.client.post(path='/api/articles/test-title12/report', data=test_report_data,
                                    HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['detail'], 'An article does not exist')
