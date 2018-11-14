'''articles/tests/test_highlight.py'''
import json
from rest_framework.views import status
from .base import BaseTest

class HighlightTestCase(BaseTest):
    '''Test case for highlighting and commenting on text in an article'''
    def test_highlight(self):
        '''test creating highlights and comments'''
        # test successful highlight and comment
        response = self.client.post(self.HIGHLIGHT, self.highlight_data,
                                    HTTP_AUTHORIZATION=self.non_user_token,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.highlight_data["comment"],
                         response.data["comment"])
        # test successful highlight
        del self.highlight_data["comment"]
        response = self.client.post(self.HIGHLIGHT, self.highlight_data,
                                    HTTP_AUTHORIZATION=self.non_user_token,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.highlight_data["index_start"],
                         response.data["index_start"])
        # test unauthenticated user
        response = self.client.post(self.HIGHLIGHT, self.highlight_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"],
                         "Authentication credentials were not provided.")
        # test missing data
        response = self.client.post(self.HIGHLIGHT, {},
                                    HTTP_AUTHORIZATION=self.non_user_token,
                                    format="json")
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["index_start"][0],
                         "This field is required.")
        self.assertEqual(response.data["errors"]["index_stop"][0],
                         "This field is required.")
        # test article not found
        response = self.client.post('/api/articles/very-weird-title/highlight/',
                                    self.highlight_data,
                                    HTTP_AUTHORIZATION=self.non_user_token,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "This article doesn't exist")
        # test index out of range
        response = self.client.post(self.HIGHLIGHT,
                                    self.out_of_index_highlight_data,
                                    HTTP_AUTHORIZATION=self.non_user_token,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["errors"][0],
                         "Text doesn't exist on this article")

    def test_get_highlights(self):
        '''test retrieving highlights'''
        # highlight and comment on first article
        self.client.post(self.HIGHLIGHT, self.highlight_data,
                         HTTP_AUTHORIZATION=self.non_user_token, format="json")
        # test get all highlights of an article
        response = self.client.get(self.HIGHLIGHT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(1, len(response.data))
        # test get single highlight by id
        response = self.client.get(self.HIGHLIGHT_ID.format(2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.highlight_data["index_start"],
                         response.data["index_start"])
        # test article not found
        response = self.client.get('/api/articles/very-weird-title/highlight/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "This article doesn't exist")
        # test highlight not found
        response = self.client.get('/api/articles/test-title/highlight/221/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "Not found.")

    def test_update_highlight(self):
        '''test updating a highlight or comment'''
        # highlight and comment on second article
        self.client.post(self.HIGHLIGHT_2, self.highlight_data, 
                         HTTP_AUTHORIZATION=self.non_user_token, format="json")

        update_highlight_data = {
            "comment": "go home!"
        }
        # test successful update comment
        response = self.client.put(self.HIGHLIGHT_ID_2.format(5),
                                   update_highlight_data,
                                   HTTP_AUTHORIZATION=self.non_user_token,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_highlight_data["comment"],
                         response.data["comment"])
        # test successful update indexes
        update_highlight_data = {
            "index_start": 2,
            "inex_stop": 15
        }
        response = self.client.put(self.HIGHLIGHT_ID_2.format(5),
                                   update_highlight_data,
                                   HTTP_AUTHORIZATION=self.non_user_token,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_highlight_data["index_start"],
                         response.data["index_start"])
        # test non-author trying to update
        response = self.client.put(self.HIGHLIGHT_ID_2.format(5),
                                   update_highlight_data,
                                   HTTP_AUTHORIZATION=self.token,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"],
                         "You do not have permission to perform this action.")
        # test unauthenticated user
        response = self.client.put(self.HIGHLIGHT_ID_2.format(5),
                                   update_highlight_data,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"],
                         "Authentication credentials were not provided.")
        # test article not found
        response = self.client.put('/api/articles/very-weird-title/highlight/1/',
                                   update_highlight_data,
                                   HTTP_AUTHORIZATION=self.non_user_token,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "Not found.")
        # test highlight not found
        response = self.client.put('/api/articles/test-title/highlight/221/',
                                   update_highlight_data,
                                   HTTP_AUTHORIZATION=self.non_user_token,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "Not found.")

    def test_delete_highlight(self):
        '''test deleting an article'''
        # highlight and comment on second article
        self.client.post(self.HIGHLIGHT_2, self.highlight_data,
                         HTTP_AUTHORIZATION=self.non_user_token,
                         format="json")
        # test non-author trying to delete
        response = self.client.delete(self.HIGHLIGHT_ID_2.format(1),
                                      HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"],
                         "You do not have permission to perform this action.")
        # test unauthenticated user
        response = self.client.delete(self.HIGHLIGHT_ID_2.format(1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"],
                         "Authentication credentials were not provided.")
        # test successful delete
        response = self.client.delete(self.HIGHLIGHT_ID_2.format(1),
                                      HTTP_AUTHORIZATION=self.non_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Comment deleted")
        # test article not found
        response = self.client.delete('/api/articles/very-weird-title/highlight/1/',
                                      HTTP_AUTHORIZATION=self.non_user_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "This article doesn't exist")
        # test highlight not found
        response = self.client.delete('/api/articles/test-title/highlight/221/',
                                      HTTP_AUTHORIZATION=self.non_user_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)["detail"], "Not found.")
