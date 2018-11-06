'''articles/views.py'''
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied

from .serializers import ArticleSerializer
from .models import Article

class ArticlesView(viewsets.ModelViewSet):
    '''Articles view for post, get, put and delete methods for articles'''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    def check_article_exists(self, slug):
        '''method checking if article exists'''
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('This article doesn\'t exist')
        
        return article

    def list(self, request):
        '''method retrieving all articles(get)'''
    queryset = Article.objects.all()
    permission_classes = (AllowAny,) #IsAuthenticatedOrReadOnly,
    serializer_class = ArticleSerializer

    def list(self, request):
        queryset = Article.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        '''method creating a new article(post)'''
        article = request.data
        email = request.user
        serializer = self.serializer_class(data=article, context={"email":email})
        article = request.data
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug):
        '''method retrieving a single article(get)'''
        article = self.check_article_exists(slug)
        serializer = self.serializer_class(article)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        '''method updating an article(put)'''
        article = self.check_article_exists(slug)
        serializer = self.serializer_class(article, data=request.data, context={"email":request.user}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        '''method deleting an article(delete)'''
        article = self.check_article_exists(slug)
        email = request.user
        if email != article.author:
            raise PermissionDenied
        article.delete()
        return Response(dict(message="Article {} deleted successfully".format(slug)), status=status.HTTP_200_OK)
    def retrieve(self, request, id):
        return Response(dict(msg="Here's a single item"))

    def update(self, request, id):
        return Response(dict(msg="We've updated the list"))

    def partial_update(self, request, id):
        return Response(dict(msg="Partial update?"))

    def destroy(self, request, id):
        return Response(dict(msg="Deleted the item!"))
