import jwt
import json

from django.conf import settings
from django.http import HttpResponse

from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication

from .models import User
from authors.settings import SECRET_KEY


class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication helper class
    :param: BaseAuthentication: 
    """
    def authenticate(self, request):
        """
        :param: request: request object to decode and authenticate
        """

        auth = get_authorization_header(request).split()

        #Check if token and is present
        if not auth or auth[0].lower() != b'token':
            return None

        #Check if the correct credemtials were passed in 'request' parameter
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        #Check if token header has correct number of segments
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)
            
        #Check if the token has an actual value
        try:
            token = auth[1]
            if token == 'null':
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
        
        #Decode token sucessfully, else catch some errors;
        #errors can be due to expired signature, in decoding
        #token validity or a user not existing
        try:
            payload = jwt.decode(token, SECRET_KEY)
            email = payload['email']
            msg = {'Error': "Token mismatch",'status' :"401"}
            
            user = User.objects.get(
                email=email,
                is_active=True
            )  
        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return HttpResponse({'Error': "Token is invalid"}, status="403")
        except User.DoesNotExist:
            return HttpResponse({'Error': "Internal server error"}, status="500")

        return (user, token)


    def authenticate_header(self, request):
        """
        :param: request: request header object to authenticate
        """
        pass
