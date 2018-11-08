from rest_framework import status

from authors.apps.profiles.tests.base_test import BaseTest


class ProfilesTest(BaseTest):

    def test_list_profiles(self):
        response = self.client.get('/profile/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_view_their_profile(self):
        response = self.client.get('/profile/mathias', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_profile(self):
        response = self.client.get('/profile/angule', format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_profile(self):
        data = {
            "username": "mathias",
            "surname": "code",
            "last_name": "duty",
            "avatar": "https://pbs.twimg.com/profile_images/670856248678596608/2yr7o6QQ_400x400.jpg",
            "bio": "codeofdutycodeofdutycodeofduty"
        }
        response = self.client.put('/profile/mathias', data, format="json")
        self.assertIn("codeofdutycodeofdutycodeofduty", response.data['bio'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
