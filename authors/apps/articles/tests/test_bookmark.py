'''articles/tests/test_highlight.py'''
import json
from rest_framework.views import status
from .base import BaseTest


class BookmarkTestCase(BaseTest):
    '''Test case for bookmarking an article'''
    def bookmark(self):
        '''bookmark an article'''
        response = self.client.put('/api/articles/test-title/bookmark/',
                                   HTTP_AUTHORIZATION=self.non_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_bookmarks(self):
        '''test retrieving all bookmarks'''
        response = self.client.get('/api/articles/bookmarks/',
                                   HTTP_AUTHORIZATION=self.non_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)

    def test_bookmark(self):
        '''test bookmarking an article'''
        # test bookmarking
        response = self.bookmark()
        self.assertEqual(response.data["message"],
                         "Article bookmarked!")
        # test unbookmarking
        response = self.bookmark()
        self.assertEqual(response.data["message"],
                         "Article removed from bookmarks!")
