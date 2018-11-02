'''tests/test_reset_password.py'''
import json
from .base import *

class ResetPasswordTestCase(BaseTest):
    ''' Class to test resetting password'''
    
    def test_forget_password(self):
        '''Test successful user forget password'''
        response = self.client.post(self.FORGOT_URL, {"email": "njery.ngigi@gmail.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)["message"],
                                    "Reset link has been successfully sent to your email. Check your spam folder if you don't find it.")

    def test_missing_email(self):
        '''Test missing email'''
        response = self.client.post(self.FORGOT_URL, {"email": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["email"][0], "This field may not be blank.")
        

    def test_invalid_email(self):
        '''Test invalid email'''
        response = self.client.post(self.FORGOT_URL, {"email": "qw"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["email"][0], "Enter a valid email address.")

    def test_unregistered_user(self):
        '''Test unregister user'''
        response = self.client.post(self.FORGOT_URL, {"email": "testing214@co.ke"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["error"][0], "A user with this email was not found.")

    def test_reset_password(self):  
        '''Test all cases of user reset password'''
        response = self.client.post(self.FORGOT_URL, {"email": "njery.ngigi@gmail.com"}, format="json")
        token = json.loads(response.content)["token"]
        RESET_URL = '/api/users/reset-password/{}/'.format(token)

        # Test very long password
        very_long_password = "qwertyuiopasdfghjklzxcvbnmhgfdsaewrfjcjgfxhgvghefnldvb7349ijd848jnjnjvbgfydfui43ufnlefknkdgifefldhfgdkfdngdgfif78rejleh7hdkfjdgjdgjfkdfhriehrnerbrgrriugyoiotgkmlgn842n3kjbjkfgig"
        response2 = self.client.post(RESET_URL, {"new_password": very_long_password, 
                                                 "confirm_password": very_long_password}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response2.content)["new_password"][0], "Password cannot be more than 128 characters")
        
        # Test missing fields
        response3 = self.client.post(RESET_URL, {}, format="json")
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response3.content)["new_password"][0], "This field is required.")
        self.assertEqual(json.loads(response3.content)["confirm_password"][0], "This field is required.")
        
        # Test missing new_password field
        response4 = self.client.post(RESET_URL, {"confirm_password": "secret123"}, format="json")
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response4.content)["new_password"][0], "This field is required.")
        
        # Test missing confirm_pasword field
        response5 = self.client.post(RESET_URL, {"new_password": "secret123"}, format="json")
        self.assertEqual(response5.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response5.content)["confirm_password"][0], "This field is required.")
        
        # Test blank Fields
        response6 = self.client.post(RESET_URL, {"new_password": "", "confirm_password": ""}, format="json")
        self.assertEqual(response6.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response6.content)["new_password"][0], "This field may not be blank.")
        self.assertEqual(json.loads(response6.content)["confirm_password"][0], "This field may not be blank.")
        
        # Test whitespaces
        response7 = self.client.post(RESET_URL, {"new_password": "   ", "confirm_password": "   "}, format="json")
        self.assertEqual(response7.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response7.content)["new_password"][0], "This field may not be blank.")
        self.assertEqual(json.loads(response7.content)["confirm_password"][0], "This field may not be blank.")

        # Test short password
        response8 = self.client.post(RESET_URL, {"new_password": "mart12", "confirm_password": "mart12"}, format="json")
        self.assertEqual(response8.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response8.content)["new_password"][0], "Password must contain at least 8 characters")
        
        # Test password with repeating characters
        response9 = self.client.post(RESET_URL, {"new_password": "aaaaaa1111", "confirm_password": "aaaaaa1111"}, format="json")
        self.assertEqual(response9.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response9.content)["new_password"][0], "Password must contain a number and a letter and that are not repeating more that two times")
        
       # Test non-alphanumeric password'''
        response10 = self.client.post(RESET_URL, {"new_password": "qwertyuiop", "confirm_password": "qwertyuiop"}, format="json")
        self.assertEqual(response10.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response10.content)["new_password"][0], "Password must contain a number and a letter and that are not repeating more that two times")

        response11 = self.client.post(RESET_URL, {"new_password": "1234567890", "confirm_password": "1234567890"}, format="json")
        self.assertEqual(response11.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response11.content)["new_password"][0], "Password must contain a number and a letter and that are not repeating more that two times")
        
        # Test passwords not matching
        response12 = self.client.post(RESET_URL, {"new_password": "secret123", "confirm_password": "mysecret123"}, format="json")
        self.assertEqual(response12.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response12.content)["error"][0], "Passwords don't match.")

        # Test successful password reset
        response13 = self.client.post(RESET_URL, {"new_password": "secret123", "confirm_password": "secret123"}, format="json")
        self.assertEqual(response13.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response13.content)["message"], "Congratulations! You have successfully changed your password.")
        
        # Test invalid token
        response13 = self.client.post(RESET_URL, {"new_password": "secret123", "confirm_password": "secret123"}, format="json")
        self.assertEqual(response13.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response13.content)["error"][0], "You either have an invalid token or the token has expired.")
        