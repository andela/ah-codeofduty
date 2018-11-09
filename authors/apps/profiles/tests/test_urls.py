from django.test import TestCase
from django.urls import reverse, resolve


class TestProfileUrls(TestCase):
    ''' Tests that URLs for profiles app exist. '''

    def test_follow_user_url(self):
        ''' Test if url for following user profile exists. '''
        url = reverse("profiles:follow",
                      args=['username'])

        self.assertEqual(resolve(url).view_name, "profiles:follow")
    
    def test_get_followers_url(self):
        ''' Test if url for getting followers user profile exists. '''
        url = reverse("profiles:followers",
                      args=['username'])

        self.assertEqual(resolve(url).view_name, "profiles:followers")

    def test_get_following_url(self):
        ''' Test if url for getting following user profile exists. '''
        url = reverse("profiles:following",
                      args=['username'])

        self.assertEqual(resolve(url).view_name, "profiles:following")