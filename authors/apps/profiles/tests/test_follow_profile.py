from authors.apps.authentication.tests.base import *
from django.conf import settings


class FollowProfileTestCase(BaseTest):
    """Test user profile"""

    def follow_user(self, token, username):
        """Helper method to follow a user """
        res = self.client.put(
            self.PROFILE_URL + username +'/follow',
            HTTP_AUTHORIZATION = 'Bearer ' + token,
            format='json'
        )
        return res
    
    def followers(self, token, username):
        """Helper method to get followers of a user """
        return self.client.get(
            self.PROFILE_URL+ username +'/followers',
            HTTP_AUTHORIZATION='Bearer ' + token,
            format='json'
        )

    def following(self, token, username):
        """Helper method to get profiles user is following"""
        return self.client.get(
            self.PROFILE_URL+ username +'/following',
            HTTP_AUTHORIZATION='Bearer ' + token,
            format='json'
        )

    def test_follow_users(self):
        """ 
        Tests a user can follow a profile 
        """
        # username : zawi
        self.register_user()

        # username : gray
        self.register_user1()

        # login zawi
        response = self.login_user()
        token = response.data['token'] 

        response = self.follow_user(token, "gray")
        self.assertTrue(response.data['following'])
        self.assertEquals(response.status_code, status.HTTP_200_OK)
    
    def test_follow_user_unauthenticated(self):
        """ 
        Tests a user can follow a profile without authentication
        """
        self.register_user()
        self.register_user1()
    
        response = self.login_user()
        token = '' 

        response = self.follow_user(token, "gray")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cant_follow_yourself(self):
        """ 
        Tests a user can follow their profile
        """
        self.register_user()     
        response = self.login_user()
        token = response.data['token'] 
        response = self.follow_user(token, "zawi")
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_follow_non_existent_user(self):
        """ 
        Tests a user can follow a non_existent profile 
        """
        self.register_user()
        self.register_user1()
    
        response = self.login_user()
        token = response.data['token'] 

        response = self.follow_user(token, "ghost_user")
        expected = 'The requested profile does not exist.'
        self.assertTrue(response.data['detail'] == expected)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user(self):
        """ 
        Tests a user can unfollow a profile 
        """
        self.register_user()
        self.register_user1()
    
        response = self.login_user()
        token = response.data['token']
        self.follow_user(token, "gray")

        response = self.follow_user(token, "gray")
        self.assertFalse(response.data['following'])
        self.assertEquals(response.status_code, status.HTTP_200_OK)
    
    def test_unfollow_non_existent_user(self):
        """ 
        Tests a user can unfollow a non_existent profile
        """
        self.register_user()
        self.register_user1()
    
        response = self.login_user()
        token = response.data['token']
        self.follow_user(token, "ghost_user")

        response = self.follow_user(token, "ghost_user")
        expected = 'The requested profile does not exist.'
        self.assertTrue(response.data['detail'] == expected)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_followers(self):
        """ 
        Tests a user can get followers of a profile
        """
        # username : zawi
        self.register_user()

        # username : gray
        self.register_user1()

        # username : shalon
        self.register_user2()

        # gray login and follow zawi
        response = self.login_user1()
        token = response.data['token'] 
        self.follow_user(token, "zawi")

        # shalon login and follow zawi
        response = self.login_user2()
        token = response.data['token'] 
        self.follow_user(token, "zawi")

        response = self.followers(token, 'zawi')
        self.assertTrue(len(response.data['followers']) == 2)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_followers_for_non_existent_user(self):
        """ 
        Tests a user can get followers of a non_existent profile
        """
        self.register_user()
        response = self.login_user()
        token = response.data['token'] 

        response = self.followers(token, 'ghost_user')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_followers_without_authentication(self):
        """ 
        Tests a user can get followers of a profile without authentication
        """
        token = ''

        response = self.followers(token, 'zawi')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_get_following(self):
        """ 
        Tests a user can get following of a profile
        """
        # username : zawi
        self.register_user()

        # username : gray
        self.register_user1()

        # username : shalon
        self.register_user2()

        # zawi login and follow gray and shalon
        response = self.login_user()
        token = response.data['token'] 
        self.follow_user(token, "gray")
        self.follow_user(token, "shalon")

        response = self.following(token, 'zawi')
        self.assertTrue(len(response.data['following']) == 2)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_following_for_non_existent_user(self):
        """ 
        Tests a user can get following of a non_existent profile
        """
        self.register_user()
        response = self.login_user()
        token = response.data['token'] 

        response = self.following(token, 'ghost_user')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_following_without_authentication(self):
        """ 
        Tests a user can get following of a profile without authentication
        """
        token = ''

        response = self.following(token, 'zawi')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
