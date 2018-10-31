import jwt
from datetime import datetime
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template

import sendgrid
import os
from sendgrid.helpers.mail import *
from django.contrib.sites.shortcuts import get_current_site
from .models import User

import os

import os

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, EmailSerializer, ResetUserPasswordSerializer
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from django.core.mail import send_mail

from .models import User

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

        sg = sendgrid.SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
        from_email = Email('codeofd@gmail.com')
        to_email = Email(user_email)
        subject = "Authors Haven Email Verification @no-reply"

        current_site = get_current_site(request)

        link = "http://" + current_site.domain + '/api/users/verify/{}/'.format(token)
        message = render_to_string('email_verification.html', context={"link":link, 'user_name':user_name})
        content = Content("text/html", message)

        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

class UserForgotPassword(APIView):
    permission_classes = (AllowAny,)
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.data['token']
            email = serializer.data['email']
            current_site = get_current_site(request)
            reset_link = "http://" + current_site.domain + '/api/users/reset-password/{}/{}'.format(token, email)
            message_body = "Copy this link into your browser to reset password {}".format(reset_link)
            send_mail('Author\'s Haven Password Reset @no-reply', message_body, 'njery.ngigi@gmail.com', ['shalon.ngigi@andela.com'], fail_silently=False)
            return Response(dict(message="Reset link has been successfully sent to your email. Check your spam folder if you don't find it."))
        return Response(serializer.errors)  

class UserResetPassword(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetUserPasswordSerializer

    def put(self, request, token, email):
        serializer = self.serializer_class(data=request.data, context={"token":token, "email":email} )
        if serializer.is_valid():
            return Response(dict(message="Congratulations! You have successfully changed your password."))
        return Response(serializer.errors)
        #TODO: Ask error messages not descriptive enough

