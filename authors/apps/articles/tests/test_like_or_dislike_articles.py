"""articles/test_like_or_dislike_articles.py"""
from rest_framework.views import status

from .base import BaseTest


class TestLikeDislikeArticles(BaseTest):
    """class testing articles likes and dislikes"""

    def create_like(self):
        return self.client.post(
            self.ARTICLE_LIKES.format(
                "new-title"),
            self.likes,
            HTTP_AUTHORIZATION=self.token2,
            format='json'
        )

    def create_dislike(self):
        return self.client.post(
            self.ARTICLE_LIKES.format(
                "new-title"),
            self.dislikes,
            HTTP_AUTHORIZATION=self.token2,
            format='json'
        )

    def test_like_dislike_articles(self):
        """test creating article"""
        article_data = {
            "title": "new title",
            "body": "mama mia is never going to England1",
            "description": "happy feet",
            "time_to_read": 1,
            "tags": ["math", "science"]
        }
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token,
            format="json")

        # test cannot like own article
        response1 = self.client.post(self.ARTICLE_LIKES.format(
            "new-title"), self.likes, HTTP_AUTHORIZATION=self.token,
            format="json")
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # test cannot dislike own article
        response2 = self.client.post(self.ARTICLE_LIKES.format(
            "new-title"), self.dislikes, HTTP_AUTHORIZATION=self.token,
            format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

        # test another user can like an article
        response3 = self.client.post(self.ARTICLE_LIKES.format(
            "new-title"), self.likes, HTTP_AUTHORIZATION=self.token2,
            format="json")
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)

        # test another user can dislike an article
        response4 = self.client.post(self.ARTICLE_LIKES.format(
            "new-title"), self.dislikes, HTTP_AUTHORIZATION=self.token2,
            format="json")
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

        # test another user cannot like an article twice
        self.create_like()
        response5 = self.create_like()
        self.assertEqual(response5.status_code, status.HTTP_400_BAD_REQUEST)

        # Test article likes count
        response6 = self.client.get(self.ARTICLE.format(
            "new-title"), format='json')
        likes_count = response6.data['likes']['count']
        old_count = 0
        self.create_like()
        self.assertNotEqual(likes_count, old_count)

        # test another user cannot dislike an article twice
        self.create_dislike()
        response7 = self.create_dislike()
        self.assertEqual(response7.status_code, status.HTTP_400_BAD_REQUEST)

        # test article dislike count
        response = self.client.get(self.ARTICLE.format(
            "new-title"), format='json')
        dislikes_count = response.data['dislikes']['count']
        old_count = 0
        self.create_dislike()
        self.assertNotEqual(dislikes_count, old_count)

        # Test disliking after liking
        self.create_like()
        response = self.create_dislike()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test liking after disliking
        self.create_dislike()
        response = self.create_like()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test unauthenticated user cannot like an article
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.post(self.ARTICLE_LIKES,
                                    self.likes,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_likes(self):
        """Test deletion like """
        article_data = {
            "title": "new title",
            "body": "mama mia is never going to England1",
            "description": "happy feet",
            "time_to_read": 1,
            "tags": ["math", "science"]
        }
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token,
            format="json")

        self.create_like()
        response = self.client.delete(self.ARTICLE_LIKES.format("new-title"),
                                      HTTP_AUTHORIZATION=self.token2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test deletion of a no like
        response = self.client.delete(self.ARTICLE_LIKES.format("new-title"),
                                      HTTP_AUTHORIZATION=self.token2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test unauthenticated user cannot delete dislike
        self.client.post(self.ARTICLE_LIKES.format("new-title"), self.dislikes,
                         format='json', HTTP_AUTHORIZATION=self.token2)
        response = self.client.delete(self.ARTICLE_LIKES.format("new-title"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
