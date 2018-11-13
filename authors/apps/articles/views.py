'''articles/views.py'''
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView

from .serializers import ArticleSerializer, CommentSerializer, CommentHistorySerializer
from .models import Article, Comment, CommentHistory
from .exceptions import ArticleDoesNotExist
from rest_framework import generics


class ArticlesView(viewsets.ModelViewSet):
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
        serializer_context = {'request': request}
        queryset = Article.objects.all()
        serializer = self.serializer_class(
            queryset, context=serializer_context, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        '''method creating a new article(post)'''
        article = request.data
        email = request.user
        serializer = self.serializer_class(
            data=article, context={"email": email})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug):
        '''method retrieving a single article(get)'''
        serializer_context = {'request': request}
        article = self.check_article_exists(slug)
        serializer = self.serializer_class(article, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        '''method updating an article(put)'''
        article = self.check_article_exists(slug)
        serializer = self.serializer_class(article, data=request.data, context={
                                           "email": request.user}, partial=True)
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


class ArticlesFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def post(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise ArticleDoesNotExist

        profile.favorite(article)

        serializer = self.serializer_class(article, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise ArticleDoesNotExist

        profile.unfavorite(article)

        serializer = self.serializer_class(article, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentsListCreateAPIView(ArticlesView):
    """Authenticated users can comment on articles"""
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer

    def create_a_comment(self, request, slug=None):
        """
        This method creates a comment to a specified article if it exist
        article slug acts as a key to find an article
        """
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(author=self.request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def fetch_all_comments(self, request, slug=None):
        """
        retrieves all the comments of an article if they exist
        if the article does not exist a Not found is returned by default
        """
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comments_found = Comment.objects.filter(article__id=article.id)
        comments_list = []
        for comment in comments_found:
            serializer = CommentSerializer(comment)
            comments_list.append(serializer.data)
            response = []
            response.append({'comments': comments_list})
        commentsCount = len(comments_list)
        if commentsCount == 0:
            return Response({"Message": "There are no comments for this article"}, status=status.HTTP_200_OK)
        elif commentsCount == 1:
            return Response(response, status=status.HTTP_200_OK)
        else:
            response.append({"commentsCount": commentsCount})
            return Response(response, status=status.HTTP_200_OK)


class CommentRetrieveUpdateDestroy(CommentsListCreateAPIView, CreateAPIView):
    """
    Class to retrieve, create, update and delete a comment
    this
    """
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthenticated)
    serializer_class = CommentSerializer
    serializer_history = CommentHistorySerializer

    def fetch_comment_obj(self):
        """
        This method fetchies comment object
        if a comment does not exist a Not found is returned.
        """
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment_set = Comment.objects.filter(article__id=article.id)

        for comment in comment_set:
            new_comment = get_object_or_404(Comment, pk=self.kwargs["id"])
            if comment.id == new_comment.id:
                self.check_object_permissions(self.request, comment)
                return comment

    def create_a_reply(self, request, slug=None, pk=None, **kwargs):
        """
        This method creates a comment reply to a specified comment if it exist
        """
        data = request.data
        context = {'request': request}
        comment = self.fetch_comment_obj()
        context['parent'] = comment = Comment.objects.get(pk=comment.id)
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def fetch_a_comment(self, request, slug=None, pk=None, **kwargs):
        """
        This method will retrieve a comment if it exist
        A comment will come with all the replies if exist.
        """
        comment = self.fetch_comment_obj()
        if comment == None:
            return Response({"message": "Comment with the specified id for this article does Not Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_a_comment(self, request, slug=None, pk=None, **kwargs):
        """
        This method will update a comment
        However it cannot update a reply
        """
        comment = self.fetch_comment_obj()
        if comment == None:
            return Response({"message": "Comment with the specified id for this article does Not Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        # print(CommentSerializer(comment).data['body'])

        old_comment = CommentSerializer(comment).data['body']
        comment_id = CommentSerializer(comment).data['id']
        parent_comment_obj = Comment.objects.only('id').get(id=comment_id)
        data = request.data
        new_comment = data['body']

        if new_comment == old_comment:
            return Response(
                {"message": "New comment same as the old existing one. "
                            "Editing rejected"},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(
            comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        edited_comment = CommentHistory.objects.create(
            comment=old_comment,
            parent_comment=parent_comment_obj)
        edited_comment.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_a_comment(self, request, slug=None, pk=None, **kwargs):
        """
        This method deletes a comment if it exists
        Replies attached to a comment to be deleted are also deleted
        """
        comment = self.fetch_comment_obj()
        if comment == None:
            return Response({"message": "Comment with the specified id for this article does Not Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({"message": {"Comment was deleted successfully"}}, status.HTTP_200_OK)


# class GetCommentHistory(viewsets.ModelViewSet):
#     lookup_url_kwarg = 'pk'
#     serializer_class = CommentHistorySerializer
#     permission_classes = (IsAuthenticated,)

#     def list(self, request, *args, **kwargs):
#         """
#         Overrides the default GET request from ListAPIView
#         Returns all comment edits for a particular comment
#         :param request:
#         :param args:
#         :param kwargs:
#         :return: HTTP Code 200
#         :return: Response
#         # """
#         print(">>>>>>>>>>>>>>>>>>>")
#         try:
#             comment = Comment.objects.get(pk=kwargs['pk'])
#         except Comment.DoesNotExist:
#             return Response(
#                 {"message": "Comment not found"},
#                 status=status.HTTP_404_NOT_FOUND)

#         self.queryset = CommentHistory.objects.filter(parent_comment=comment)

#         return generics.ListAPIView.list(self, request, *args, **kwargs)


class CommentHistoryAPIView(generics.ListAPIView):
    lookup_url_kwarg = 'pk'
    serializer_class = CommentHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Overrides the default GET request from ListAPIView
        Returns all comment edits for a particular comment
        :param request:
        :param args:
        :param kwargs:
        :return: HTTP Code 200
        :return: Response
        # """

        try:
            comment = Comment.objects.get(pk=kwargs['id'])
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND)
        self.queryset = CommentHistory.objects.filter(parent_comment=comment)

        return generics.ListAPIView.list(self, request, *args, **kwargs)
