import os
import jwt
import sendgrid

from datetime import datetime
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from social_django.utils import load_backend, load_strategy
from social_core.exceptions import AuthAlreadyAssociated, MissingBackend
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string, get_template
from django.shortcuts import render
from sendgrid.helpers.mail import *

from authors.settings import SECRET_KEY
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, EmailSerializer, ResetUserPasswordSerializer, SocialSignInSignOutSerializer
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework.views import APIView
from .backends import JWTAuthentication

from django.core.mail import send_mail


class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_email = serializer.data.get('email', None)
        user_name = serializer.data.get('username', None)

        payload = {'email': user_email}
        token = jwt.encode(payload, SECRET_KEY).decode("UTF-8")

        from_email, to_email = 'codeofd@gmail.com', [user_email]
        subject = "Authors Haven Email Verification @no-reply"

        current_site = get_current_site(request)

        link = "http://" + current_site.domain + \
            '/api/users/verify/{}/'.format(token)
        message = render_to_string('email_verification.html', context={
                                   "link": link, 'user_name': user_name})

        send_mail(subject, '', from_email, to_email, html_message=message)

        return Response(dict(email=user_email, username=user_name, token=token), status=status.HTTP_201_CREATED)


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyAPIView(CreateAPIView):
    serializer_class = UserSerializer

    def get(self, request, token):
        email = jwt.decode(token, SECRET_KEY)['email']
        user = User.objects.get(email=email)
        user.is_confirmed = True
        user.save()

        return Response("Email Confirmed Successfully")


class UserForgotPassword(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = EmailSerializer

    def get(self, request):
        '''get method renders forgot password form'''
        return render(request, 'forgot_password_form.html', {})

    def post(self, request):
        '''post method sends a link with a token to email'''
        serializer = self.serializer_class(data=request.data)
        # check that data from request is valid
        if serializer.is_valid():
            token = serializer.data['token']
            email = serializer.data['email']
            username = serializer.data['username']

            time = datetime.now()
            time = datetime.strftime(time, '%d-%B-%Y %H:%M')
            current_site = get_current_site(request)
            reset_link = 'http://' + current_site.domain + \
                '/api/users/reset-password/{}/'.format(token)
            subject, from_email, to = 'Authors Haven Password Reset @no-reply', 'codeofd@gmail.com', [
                email]

            html_content = render_to_string('reset_email.html', context={
                                            "reset_link": reset_link, "username": username, "time": time})
            send_mail(subject, '', from_email, to, html_message=html_content)

            return Response(dict(message="Reset link has been successfully sent to your email. Check your spam folder if you don't find it.",
                                 token=token))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetPassword(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetUserPasswordSerializer

    def get(self, request, token):
        return render(request, 'reset_password_form.html', context={"token": token})

    def post(self, request, token):
        serializer = self.serializer_class(
            data=request.data, context={"token": token})
        if serializer.is_valid():
            return Response(dict(message="Congratulations! You have successfully changed your password."))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialSignInSignOut(CreateAPIView):
    """ this class implement the logic to allow users to login or signup using
    social accounts such as facebook, goole or twitter...."""

    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialSignInSignOutSerializer
    # allow everyone to view without having to be authenticated
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data['provider']

        # If this request was made with an authenticated user, try to associate this social
        # account with it
        authed_user = request.user if not request.user.is_anonymous else None
        strategy = load_strategy(request)

        # Get the backend that is associated with the user provider i.e google,twitter and facebook
        backend = load_backend(
            strategy=strategy, name=provider, redirect_uri=None)

        if isinstance(backend, BaseOAuth1):
           # cater for services that use OAuth1, an example is twitter
            token = {
                # 'oauth_token': serializer.data['access_token'],
                'oauth_token': serializer.data['access_token'],
                'oauth_token_secret': serializer.data['access_token_secret'],
            }

        elif isinstance(backend, BaseOAuth2):
            # we just need to pass access_token for OAuth2
            token = serializer.data['access_token']

        try:
            # check if the user exists, if exists,we just login but if not we creates a new user
            user = backend.do_auth(token, user=authed_user)

        except AuthAlreadyAssociated:
            return Response({"error": "The email is already registered, please try another one"},
                            status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            serializer = UserSerializer(user)
            user.is_verified = True
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                # Google for example will return the access_token in its response to you.
                auth_created.extra_data['access_token'] = token
                auth_created.save()
                serializer.save()
                user.save()
            # get current user id from the database.
            user_id = User.objects.values_list('id', flat=True).get(
                email=serializer.data['email'])
            serializer.instance = user
            token = JWTAuthentication.encode_token(self,
                                                   user_id)
            # a responce dictionary that has email, username and token
            response = {
                'user_id': user_id,
                'email': serializer.data['email'],
                'username': serializer.data['username'],
                'token': token
            }
            headers = self.get_success_headers(serializer.data)
            return Response(response, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            return Response({"error": "Something went wrong with the authentication, please try again"},
                            status=status.HTTP_400_BAD_REQUEST)
