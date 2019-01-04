'''articles/test_articles.py'''
import json
from rest_framework.views import status
from ..serializers import ArticleSerializer
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
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(article_data["title"],
                         json.loads(response.content)["title"])
        # test missing fields
        del article_data["title"]
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)[
                         "errors"]["title"][0], "This field is required.")
        # test very long title
        article_data["title"] = "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjkzxcvbnmqwertyuiopasdfghjklxcvbnmqwertyuiopasdfghjklzxcvbnm"
        response = self.client.post(
            self.ARTICLES, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)[
                         "errors"]["title"][0], "Ensure this field has no more than 100 characters.")
        # test unlogged in user (missing authorization header)
        article_data["title"] = "new title"
        response = self.client.post(self.ARTICLES, article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content)[
                         "detail"], "Authentication credentials were not provided.")

    def test_get_all_articles(self):
        '''test get all articles'''
        # test successful get
        response = self.client.get(self.ARTICLES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(json.loads(response.content)), 0)
        # test get popular artcles
        response = self.client.get(self.ARTICLE.format("popular"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(json.loads(response.content)), 0)
        # test get recent artcles
        response = self.client.get(self.ARTICLE.format("recent"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(json.loads(response.content)), 0)

    def test_get_user_articles(self):
        '''test get a user's articles'''
        response = self.client.get('/api/profiles/test_user/articles')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(json.loads(response.content)), 0)

    def test_get_single_article(self):
        '''test get single article'''
        # test successful get
        response = self.client.get(self.TESTARTICLE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_article_data["title"], json.loads(
            response.content)["title"])

        # test non-existent article
        response = self.client.get(self.ARTICLE.format("never-the-new-one"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertGreaterEqual(json.loads(response.content)[
                                "detail"], "This article doesn't exist")

    def test_update_article(self):
        '''test update article'''
        # test successful update
        article_data = {
            "title": "The very newest title",
        }
        response = self.client.put(
            self.TESTARTICLE, article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(article_data["title"],
                      json.loads(response.content)["title"])
        # test non-author
        response = self.client.put(
            self.TESTARTICLE, article_data, HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content)[
                         "detail"], "You do not have permission to perform this action.")
        # test non-existent article
        response = self.client.put(self.ARTICLE.format(
            "never-the-newest-title"), article_data, HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)[
                         "detail"], "This article doesn't exist")

    def test_delete_article(self):
        '''test delete article'''
        # test non-author
        response = self.client.delete(self.ARTICLE.format(
            "test-title1"), HTTP_AUTHORIZATION=self.non_user_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content)[
                         "detail"], "You do not have permission to perform this action.")
        # test successful delete
        response = self.client.delete(self.ARTICLE.format(
            "test-title1"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)[
                         "message"], "Article test-title1 deleted successfully")
        # test non-existent article
        response = self.client.delete(self.ARTICLE.format(
            "test-title1"), HTTP_AUTHORIZATION=self.token, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)[
                         "detail"], "This article doesn't exist")

    def test_favorite_article(self):
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
        response = self.favorite_article('test-title12', token)
        self.assertTrue(response.data['favorited'])
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_unfavorite_article(self):
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
        response = self.unfavorite_article('test-title12', token)
        self.assertFalse(response.data['favorited'])
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_favorite_non_existent_article(self):
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
        response = self.favorite_article('ghost slug', token)
        self.assertTrue(response.data['detail'],
                        'An article with this slug was not found.')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfavorite_non_existent_article(self):
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
        response = self.unfavorite_article('ghost slug', token)
        self.assertTrue(response.data['detail'],
                        'An article with this slug was not found.')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_favorite_article(self):
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
        response = self.favorite_article('ghost slug', token)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_time_to_read(self):
        '''test time to read articles method'''
        text = "Beneath the unstable acquaintance strikes the fleet thumb.\
        A height peers outside whatever answer. Behind the automatic tragedy\
        speculates an amended girl. The closing brush coasts. Does a mum club\
        skip? How can the agony cope? How can the elite sneak hope over the\
        dip? A half memory staggers. A populace spins the line. A sacrifice\
        produces a polar whale. My misuse misguides the cyclist.\
        The rival gutters a celebrated hospital.A part universal takes\
        the alien. The champion tool shouts. The relative crowds the sentient.\
        Why can't the secretary parade past the integrate scotch?\
        Beneath the unstable acquaintance strikes the fleet thumb. A height\
        peers outside whatever answer. Behind the automatic tragedy speculates\
        an amended girl. The closing brush coasts. Does a mum club skip? How\
        can the agony cope?How can the elite sneak hope over the dip?\
        A half memory staggers. A populace spins the line. A sacrifice\
        produces a polar whale. My misuse misguides the cyclist. The rival\
        gutters a celebrated hospital. A part universal takes the alien.\
        The champion tool shouts. The relative crowds the sentient.\
        Why can't the secretary parade past the integrate scotch?Beneath the\
        unstable acquaintance strikes the fleet thumb. A height peers outside\
        whatever answer. Behind the automatic tragedy speculates an amended\
        girl. The closing brush coasts. Does a mum club skip?"

        images = ["test_image_url.jpg", "test_image_url_2.jpg"]

        serializer = ArticleSerializer()
        self.assertEqual(serializer.get_time_to_read(text, images), 2)

    def test_if_article_returns_share_links(self):
        """This method tests whether the API returns share links"""
        res = self.client.get(self.TESTARTICLE)
        self.assertIn("facebook", json.loads(res.content))
        self.assertIn("Linkedin", json.loads(res.content))
        self.assertIn("twitter", json.loads(res.content))
        self.assertIn("mail", json.loads(res.content))
        self.assertIn("url", json.loads(res.content))

    def test_get_tags(self):
        """Tests whether we can get all article tags"""
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
        response = self.get_article_tags()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected_tag = response.data['tags'][0]
        self.assertEqual(expected_tag, 'TDD')

    def test_article_payload_tag(self):
        """Tests whether article payload has tags upon creating"""
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
        self.assertTrue(response.data['tagList'])
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        tag_in_payload = response.data['tagList'][0]
        self.assertEqual(tag_in_payload, 'TDD')
