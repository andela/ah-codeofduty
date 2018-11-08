"""
Rating Articles Views module
"""

from django.shortcuts import render

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, viewsets

from ..authentication.renderers import JSONRenderer

from .serializers import RateSerializers
from .models import Rating


class RateArticleView((viewsets.ModelViewSet)):
    """
    Rate Articles view class
    :param:viewsets.ModelViewSet:
    """
    queryset = Rating.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RateSerializers

    def create(self, request, slug):
        """
        create a rating
        :params: request: rating request
        :param:slug: url field
        :return: 201 response status code with data
        """
        rating = request.data
        user = request.user
        serializer = self.serializer_class(data=rating, context={'slug': slug, 'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
