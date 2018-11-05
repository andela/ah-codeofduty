from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from authors.apps.profiles.renderers import ProfileJSONRenderer
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import User, Profile


class ProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Users are able to edit their profile information
    """
    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        serializer = self.serializer_class(user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, username, *args, **kwargs):
        serializer_data = request.data.get('profiles', {})
        user = get_object_or_404(User, username=username)

        serializer_data = {
            'surname': serializer_data.get('surname', request.user.profile.surname),
            'last_name': serializer_data.get('last_name', request.user.profile.last_name),
            'avatar': serializer_data.get('avatar', request.user.profile.avatar),
            'bio': serializer_data.get('bio', request.user.profile.bio),
        }

        serializer = self.serializer_class(
            request.user.profile,
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
        pagination_class = LimitOffsetPagination

        def list(self, request):
            serializer_context = {'request': request}
            page = self.paginate_queryset(self.queryset)
            serializer = self.serializer_class(
                page,
                context=serializer_context,
                many=True
            )
            return self.get_paginated_response(serializer.data)
