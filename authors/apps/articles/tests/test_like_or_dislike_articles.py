from .base import BaseTest
from rest_framework.views import status


class CommentsLikeDislikeTestCase(BaseTest):
    """test class for liking and disliking comments """

    def get_token(self):
        response = self.client.post(self.SIGN_UP_URL, self.fav_test_user, format='json')
        response = self.client.post(self.SIGN_IN_URL, self.fav_test_user, format='json')
        token = response.data['token']
        return token

    def create_article(self, token, article):
        """ Method to create an article"""
        return self.client.post(self.ARTICLES, self.test_article_data,
                                HTTP_AUTHORIZATION='Bearer ' + token, format='json')

    def test_articles(self):
        """Test test the liking of an article"""
        token = self.get_token()
        article_data = {
            "title": "test title",
            "body": "This is me testing",
            "description": "testing",
            "time_to_read": 1,
            "tags": ["TDD"]
        }
        # article created
        response = self.create_article(token, article_data)
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        slug = response.data['slug']

        # like an article
        response = self.client.put('/api/articles/' + str(slug) + '/like/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # un-like an article
        response = self.client.put('/api/articles/' + str(slug) + '/like/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # dislike an article
        response = self.client.put('/api/articles/' + str(slug) + '/dislike/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # un-dislike an article
        response = self.client.put('/api/articles/' + str(slug) + '/dislike/',
                                   HTTP_AUTHORIZATION=self.token, format='json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        # like missing article
        response = self.client.put('/api/articles/me/like/',
                                   HTTP_AUTHORIZATION='Bearer ' + token,
                                   format='json'
                                   )
        self.assertEquals(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEquals(response.data['Error'], 'The article does not exist')

        # dislike missing article
        response = self.client.put('/api/articles/me/dislike/',
                                   HTTP_AUTHORIZATION='Bearer ' + token,
                                   format='json'
                                   )
        self.assertEquals(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEquals(response.data['Error'], 'The article does not exist')
