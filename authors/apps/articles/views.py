'''articles/views.py'''
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework import status, viewsets

from .serializers import ArticleSerializer
from .models import Article

class ArticlesView(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    permission_classes = (AllowAny,) #IsAuthenticatedOrReadOnly,
    serializer_class = ArticleSerializer

    def list(self, request):
        queryset = Article.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        article = request.data
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, id):
        return Response(dict(msg="Here's a single item"))

    def update(self, request, id):
        return Response(dict(msg="We've updated the list"))

    def partial_update(self, request, id):
        return Response(dict(msg="Partial update?"))

    def destroy(self, request, id):
        return Response(dict(msg="Deleted the item!"))
