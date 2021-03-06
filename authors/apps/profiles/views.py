from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.views import APIView
from authors.apps.core.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404

from authors.apps.profiles.renderers import ProfileJSONRenderer
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from .exceptions import ProfileDoesNotExist


class ProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Users are able to edit their profile information
    """
    permission_classes = (IsAuthenticated, AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(
            user.profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, username, *args, **kwargs):
        serializer_data = request.data
        user = get_object_or_404(User, username=username)
        serializer_data = {
            'surname': serializer_data.get('surname', request.user.profile.surname),
            'last_name': serializer_data.get('last_name', request.user.profile.last_name),
            'avatar': serializer_data.get('avatar', request.user.profile.avatar),
            'bio': serializer_data.get('bio', request.user.profile.bio),
        }

        serializer = self.serializer_class(
            request.user.profile, context={'request': request},
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user.profile, serializer_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileList(ListAPIView):
    """View all created profiles"""
    permission_classes = (AllowAny,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProfileFollowAPIView(APIView):
    """
    implements functionality to follow and unfollow a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def put(self, request, username=None):
        """
        method to follow and unfollow a user
        """
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        if follower.pk is followee.pk:
            raise serializers.ValidationError('You cannot follow yourself')

        if follower.is_following(followee) is False:
            follower.follow(followee)
        else:
            follower.unfollow(followee)

        serializer = self.serializer_class(
            followee, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersAPIView(APIView):
    """
    implements functionality to get followers of a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get(self, request, username):
        """
        method to get a user's followers
        """
        user = self.request.user.profile

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        followers = user.get_followers(profile)
        serializer = self.serializer_class(
            followers, many=True, context={'request': request})
        return Response({"followers": serializer.data}, status=status.HTTP_200_OK)


class FollowingAPIView(APIView):
    """
    implements functionality to get profiles a user is following
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get(self, request, username):
        """
        method to get profiles a user is following
        """
        user = self.request.user.profile

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        following = user.get_following(profile)
        serializer = self.serializer_class(
            following, many=True, context={'request': request})
        return Response({"following": serializer.data}, status=status.HTTP_200_OK)


class UserArticlesView(ListAPIView):
    pagination_class = LimitOffsetPagination

    def get(self, request, username):
        user = User.objects.get(username=username)
        articles = Article.objects.filter(author=user.id)
        page = self.paginate_queryset(articles)
        serializer = ArticleSerializer(page, context={'request': request},
                                       many=True)

        return self.get_paginated_response(serializer.data)
