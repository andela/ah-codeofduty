"""
JWT Configuration module
"""
import jwt
import os

from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse

from rest_framework import authentication, exceptions
from rest_framework.authentication import (
    get_authorization_header,
    BaseAuthentication)

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

        # Check if token and is present
        if not auth or auth[0].lower() != b'bearer':
            return None

        # Check if the correct credentials were passed in 'request' parameter
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        # Check if token header has correct number of segments
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        # Decode token successfully, else catch some errors;
        # errors can be due to expired signature, in decoding
        # token validity or a user not existing

        token = auth[1]
        user = None
        try:
           user = decode_token(token)
        # Except custom errors while using the token
        except Exception as e:
            if e.__class__.__name__ == 'DecodeError':
                raise exceptions.AuthenticationFailed('cannot decode token')
            if e.__class__.__name__ == 'ExpiredSignatureError':
                raise exceptions.AuthenticationFailed('Token has expired')
        return (user, token)

    def authenticate_header(self, request):
        """
        Authenticate header prefix
        :param: request: object request to add prefix
        """
        return 'Bearer'

    def encode_token(self, user_id):
        """
        This method gerate token by encoding registered user
        email address
        """
        payload = {
            'id': user_id,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY).decode('UTF-8')

def decode_token(token):
    """decode token helper"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    payload = jwt.decode(token, SECRET_KEY)
    pk = payload['id']
    user = User.objects.get(
        pk=pk
    )
    return user