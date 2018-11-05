"""tests/test user authentication"""
from .base import *

class ViewTestCase(BaseTest):
    """Test user views"""

    def test_user_registration_email_exists(self):
        """Test user with that email already exists"""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_email_exists,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_user(self):
        """Test user signup capability."""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_username_exists(self):
        """Test user with that username already exists"""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_username_exists,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_fields(self):
        """Test user registers with missing fields"""

        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_missing_fields,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_username_parameter(self):
        """Test user registers with missing username parameter"""

        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_missing_username_parameter,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_email_parameter(self):
        """Test user registers with missing email parameter"""

        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_missing_email_parameter,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_short_password(self):
        """Test user registers with short password"""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_inputs_short_password,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_invalid_email(self):
        """Test user registers invalid email"""

        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_inputs_invalid_email,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Test the api has user login capability."""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_IN_URL,
            self.user_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_wrong_password(self):
        """Test wrong login credentials."""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_IN_URL,
            self.user_wrong_password,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_non_existent(self):
        """Test if user does not exist"""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_IN_URL,
            self.user_does_not_exist,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password(self):
        """Test missing password on registration."""
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        response = self.client.post(
            self.SIGN_IN_URL,
            self.missing_password,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email(self):
        '''Test verify email'''
        response = self.client.post(
            self.SIGN_UP_URL,
            self.user_data,
            format="json")
        content = json.loads(response.content)
<<<<<<< HEAD
        token = content['user']['verify_token']
=======
        token = content['user']['token']
>>>>>>> 54221bc... #161255355 Reset Password  (#16)
        VERIFY_URL = '/api/users/verify/{}/'.format(token)
        response = self.client.get(VERIFY_URL)
        self.assertEqual(json.loads(response.content), 'Email Confirmed Successfully')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
