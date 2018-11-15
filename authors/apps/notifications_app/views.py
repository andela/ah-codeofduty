"""
Notification views serializer
"""

import jwt

from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.contrib.sites.shortcuts import get_current_site

from notifications.models import Notification

from .serializers import NotificationSerializer

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.authentication.renderers import UserJSONRenderer
from authors.apps.authentication.backends import decode_token, JWTAuthentication

from authors.settings import SECRET_KEY

class UserAllNotificationsView(ListAPIView):
    """
    Get all user notifications class
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = NotificationSerializer
    renderer_class = (UserJSONRenderer)

    def get(self, request):
        """
        Get all user notifications method
        :return: a list of all user notifications if
          user is subscribed to notifications, else a
          message to notify the user they aren't
          subscribed
        """
        serializer_context = {'request': request}
        user = request.user
        if user.is_authenticated:
            queryset = user.notifications.all()
            serializer = self.serializer_class(
                queryset, context=serializer_context, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'message': 'you are not subscribed to notifications'},
            status=status.HTTP_200_OK)

class ReadNotifications(APIView):
    """
    Mark a specific notification as read class
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = NotificationSerializer

    def put(self, request, pk):
        """
        Mark a specific notification  as read method
        :param: request: user request
        :pk: the id of the notification to be read
        :return: a message to notify a user has read
          a notification, else a message to
          notify the user they aren't subscribed
        """
        user = request.user
        if user.is_subscribed:
            notification = Notification.objects.get(id=pk)
            notification.mark_as_read()
            return Response(
                {'message': 'Notification has been read'},
                status=status.HTTP_200_OK)
        return Response(
            {'message': 'you are not subscribed to notifications'},
            status=status.HTTP_200_OK)


class UserReadNotifications(ListAPIView):
    """
    Get all read notifications class
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = NotificationSerializer

    def get(self, request):
        """
        Get all read notifications method
        :return: a list of all read notifications if
          user is subscribed to notifications, else a
          message to notify the user they aren't
          subscribed
        """
        serializer_context = {'request': request}
        user = request.user
        if user.is_subscribed:
            queryset = user.notifications.read()
            serializer = self.serializer_class(
                queryset, context=serializer_context, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'message': 'you are not subscribed to notifications'},
            status=status.HTTP_200_OK)

class UserUnReadNotifications(ListAPIView):
    """
    Get all unread notifications class
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = NotificationSerializer

    def get(self, request):
        """
        Get all unread notifications method
        :return: a list of all unread notifications if
          user is subscribed to notifications, else a
          message to notify the user they aren't
          subscribed
        """
        serializer_context = {'request': request}
        user = request.user
        if user.is_subscribed:
            queryset = user.notifications.unread()
            serializer = self.serializer_class(
                queryset, context=serializer_context, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'message': 'you are not subscribed to notifications'},
            status=status.HTTP_200_OK)

class Subscription(APIView):
    """
    In-app and Email subscription class
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_class = (UserJSONRenderer)


    def post(self, request):
        """
        Subscription method
        :param: request: user request to subscribe to notifications
          if unsubscribed and to unsubscribe if subscribed to
          inapp an email notifications
        """
        user = request.user
        token = JWTAuthentication.encode_token(self, user.pk)
        if user.is_subscribed:
            user.is_subscribed = False
            user.save()
            note_response = {
                'message': 'You have successfully unsubscribed from notifications'}

            # Setup the content to be sent
            # the url to send with the mail
            current_site = get_current_site(request)
            link = "http://" + current_site.domain + \
            '/api/notifications/subscription/'+token+'/'

            from_email = 'codeofd@gmail.com'
            username = request.user.username
            template='unsubscribe.html'
            to = [request.user.email]
            subject='Email notification subscription'
            html_content = render_to_string(template, context={
                                             "username": username,
                                             "subscribe_url":link})
            #send Email
            send_mail(subject, '', from_email, to, html_message=html_content)
            return  Response(note_response, status=status.HTTP_200_OK)

        if not user.is_subscribed:
            user.is_subscribed = True
            user.save()
            note_response = {
                'message': 'You have successfully subscribed to notifications'}

            # Setup the content to be sent
            # the url to send with the mail
            current_site = get_current_site(request)
            link = "http://" + current_site.domain + \
            '/api/notifications/subscription/'+token+'/'

            from_email = 'codeofd@gmail.com'
            username = request.user.username
            template='subscribe.html'
            to = [request.user.email]
            subject='Email notification subscription'
            html_content = render_to_string(template, context={
                                             "username": username,
                                             "unsubscribe_url":link})
            #send Email
            send_mail(subject, '', from_email, to, html_message=html_content)
            return  Response(note_response, status=status.HTTP_200_OK)


class SubscriptionEmailAPIView(APIView):
    """
    Email subscription confirmation class
    """
    permission_classes = (AllowAny,)

    def post(self, request, token):
        """
        Email subscription confirmation method
        :param: request: user request
        :param: token: user token to be deceded to a
          user object in order for the user to be  confirmed
          to exist and is active, hence set their subscription
          status
        """
        user = decode_token(token)
        if not user.is_subscribed:
            user.is_subscribed = True
            user.save()
            return Response(
                {"message": "Successfully Subscribed to email notifications"},
                status=status.HTTP_200_OK)
        user.is_subscribed = False
        user.save()
        return Response(
            {"message": "Successfully Unsubscribed from email notifications"},
            status=status.HTTP_200_OK)
