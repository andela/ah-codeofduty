'''articles/test_articles.py'''
import json
from rest_framework.views import status
from .base import BaseTest


class ArticleTestCase(BaseTest):
    '''class testing CRUD functions for articles'''

    def test_create_read_update_delete_comments(self):
        '''test creating article'''
        # test successful creating article
        article_data = {
            "title": "new title",
            "body": "mama mia is never going to England1",
            "description": "happy feet",
            "time_to_read": 1,
            "tags": ["math", "science"]
        }
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")

    # sample test data
        sample_comment = {"body": "this is a sample comment"}
        sample_comment_reply = {"body": "this is a sample comment reply"}
        sample_comment_update = {"body": "this is a sample comment update"}

    # test comment can be created to an existing article
        res1 = self.client.post(self.CREATE_A_COMMENT.format(
            "new-title"), sample_comment, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

    # test comment can be fetched for all
        res2 = self.client.get(self.FETCH_ALL_COMMENTS.format(
            "new-title"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    # test a reply can be created to an existing article
        res3 = self.client.post(self.CREATE_A_REPLY.format(
            "new-title", 1), sample_comment_reply, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)

    # test can fetch a comment and all its replies
        res4 = self.client.get(self.FETCH_A_COMMENT.format(
            "new-title", 1), sample_comment, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res4.status_code, status.HTTP_200_OK)

    #  test non existing comment
        res44 = self.client.get(self.FETCH_A_COMMENT.format(
            "new-title", 5), sample_comment, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res44.status_code, status.HTTP_404_NOT_FOUND)

    # update a comment
        res5 = self.client.put(self.UPDATE_A_COMMENT.format(
            "new-title", 1), sample_comment_update, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res5.status_code, status.HTTP_201_CREATED)

    # update a no existing comment
        res55 = self.client.put(self.UPDATE_A_COMMENT.format(
            "new-title", 34), sample_comment_update, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res55.status_code, status.HTTP_404_NOT_FOUND)

    # delete a comment
        res6 = self.client.delete(self.DELETE_A_COMMENT.format(
            "new-title", 1), sample_comment_update, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res6.status_code, status.HTTP_200_OK)

    # fetch all comments
        res22 = self.client.get(self.FETCH_ALL_COMMENTS.format(
            "new-title"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res22.status_code, status.HTTP_200_OK)

    # test comment can be created to an existing article
        res22 = self.client.get(self.FETCH_ALL_COMMENTS.format(
            "new-title"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res22.status_code, status.HTTP_200_OK)

        res222 = self.client.get(self.FETCH_ALL_COMMENTS.format(
            "new-title45"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res222.status_code, status.HTTP_404_NOT_FOUND)

        res11 = self.client.post(self.CREATE_A_COMMENT.format(
            "new-title"), sample_comment, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res11.status_code, status.HTTP_201_CREATED)

        res111 = self.client.post(self.CREATE_A_COMMENT.format(
            "new-title"), sample_comment, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res111.status_code, status.HTTP_201_CREATED)

        res222 = self.client.get(self.FETCH_ALL_COMMENTS.format(
            "new-title"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(res222.status_code, status.HTTP_200_OK)
