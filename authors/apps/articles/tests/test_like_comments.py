from .base import BaseTest
from authors.apps.articles.models import Article
from rest_framework.views import status
import json


class CommentsLikeDislikeTestCase(BaseTest):
    """test class for liking and disliking comments """

    def create_article(self, token, article):
        """ Method to create an article"""
        return self.client.post(self.ARTICLES, self.test_article_data,
                                HTTP_AUTHORIZATION=self.token, format='json')

    def create_comment(self, token, slug, test_comment_data):
        """ Method to create an article then comment"""
        self.client.post(self.ARTICLES, self.test_article_data,
                         HTTP_AUTHORIZATION=self.token, format='json')
        return self.client.post('/api/articles/test-title12/comment/', self.test_comment_data,
                                HTTP_AUTHORIZATION=self.token, format='json')

    def test_like_comment(self):
        """Test test the liking of a comment"""
        # article created
        response = self.create_article(self.token, self.test_article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        # creating a comment
        slug = response.data['slug']

        response = self.create_comment(self.token, slug, self.test_comment_data)

        comment_id = response.data["id"]
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        # like a comment
        response = self.client.put('/api/articles/test-title12/comment/' + str(comment_id) + '/like/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_unlike_comment(self):
        """Test test the liking of a comment"""
        response = self.create_article(self.token, self.test_article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        slug = response.data['slug']

        response = self.create_comment(self.token, slug, self.test_comment_data)
        comment_id = response.data["id"]
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        response = self.client.put('/api/articles/test-title12/comment/' + str(comment_id) + '/like/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_like_missing_article(self):
        """Test test the liking of a comment"""
        response = self.create_article(self.token, self.test_article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        slug = response.data['slug']

        response = self.create_comment(self.token, slug, self.test_comment_data)
        comment_id = response.data["id"]
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        response = self.client.put('/api/articles/me/comment/' + str(comment_id) + '/dislike/',
                                   HTTP_AUTHORIZATION=self.token,
                                   format='json'
                                   )
        self.assertEquals(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_like_missing_comment(self):
        """Test test the liking of a comment"""
        response = self.create_article(self.token, self.test_article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        slug = response.data['slug']

        response = self.create_comment(self.token, slug, self.test_comment_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)

        response = self.client.put('/api/articles/test-title12/comment/99/dislike/',
                                   HTTP_AUTHORIZATION=self.token,
                                   format='json'
                                   )
        self.assertEquals(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_like_comment_if_article_does_not_exist(self):
        """Test test the liking of a comment in an article that does not exist"""
        slug = 'test-title12'

        response = self.create_comment(self.token, slug, self.test_comment_data)
        comment_id = response.data["id"]
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        # like a comment
        response = self.client.put('/api/articles/test-title123/comment/' + str(comment_id) + '/like/',
                                   HTTP_AUTHORIZATION=self.token,
                                   format='json'
                                   )
        self.assertEquals(response.data['Error'], 'The article does not exist')
