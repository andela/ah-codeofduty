'''articles/views.py'''
import django_filters
from django.contrib.postgres.fields import ArrayField
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, generics
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.renderers import ReportJSONRenderer
from authors.apps.core.pagination import LimitOffsetPagination
from .models import Article, Comment, CommentHistory, Highlight, Report, LikesDislikes, Tag

from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.contrib.sites.shortcuts import get_current_site

from .serializers import (ArticleSerializer, CommentSerializer, TagSerializer,
                          CommentHistorySerializer, HighlightSerializer, ReportSerializer, LikesDislikesSerializer)
from .models import Article, Comment
from .exceptions import ArticleDoesNotExist
from authors.apps.authentication.models import User
from authors.apps.authentication.backends import decode_token, JWTAuthentication


class ArticleMetaData:
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer

    def check_article_exists(self, slug):
        '''method checking if article exists'''
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('This article doesn\'t exist')

        return article


class ArticlesView(ArticleMetaData, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        ''' method to filter article by author, title, and tag '''
        queryset = Article.objects.all()

        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author__username=author)

        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title=title)

        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        return queryset

    def list(self, request):
        ''' method to fetch all articles'''
        serializer_context = {'request': request}

        page = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(
            page, context=serializer_context, many=True)
        return self.get_paginated_response(serializer.data)

    def list_by_recent(self, request):
        page = self.paginate_queryset(self.get_queryset().order_by('-time_created'))
        serializer = self.serializer_class(
            page, context={"request": request}, many=True)
        return self.get_paginated_response(serializer.data)

    def list_by_popular(self, request):
        page = self.paginate_queryset(self.get_queryset().order_by('-average_rating'))
        serializer = self.serializer_class(
            page, context={"request": request}, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        '''method creating a new article(post)'''
        serializer = self.serializer_class(
            data=request.data, context={"email": request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        profile = self.request.user.profile
        to = []
        my_followers = profile.get_my_followers()

        for follower in my_followers:
            subscribed = User.objects.filter(username=follower).values()[0]['is_subscribed']
            if subscribed:
                follower = User.objects.filter(username=follower).values()[0]['email']
                to.append(follower)

        for recipient in to:
            pk = User.objects.filter(email=recipient).values()[0]['id']
            token = JWTAuthentication.encode_token(self, pk)

            current_site = get_current_site(request)

            # Setup the content to be sent
            # the url to send with the mail
            link = "http://" + current_site.domain + \
            '/api/notifications/subscription/'+token+'/'
            article_link = "http://" + current_site.domain + \
            '/api/articles/{}/'.format(serializer.data['slug'])

            from_email = 'codeofd@gmail.com'
            #username = request.user.username
            template='index.html'
            subject='"{}" added a new article "{}"'.format(request.user.username, request.data['title'])

            username = User.objects.filter(email=recipient).values()[0]['username']
            html_content = render_to_string(template, context={
                                                "username": username,
                                                "author": request.user.username,
                                                "unsubscribe_url":link,
                                                "article_link": article_link,
                                                "article_title":request.data['title']})
            send_mail(subject, '', from_email, [recipient], html_message=html_content)

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
    """
    Implements favoriting and unfavoriting articles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

    def post(self, request, slug=None):
        """
        method to favorite an article
        """
        profile = self.request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise ArticleDoesNotExist

        profile.favorite(article)

        serializer = self.serializer_class(article, context=serializer_context)

        article_author_id = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['author_id']
        article_username = User.objects.filter(id=article_author_id).values()[0]['username']
        article_username_pk = User.objects.filter(id=article_author_id).values()[0]['id']
        article_author = User.objects.filter(id=article_author_id).values()[0]['email']
        article_title = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['title']
        author_notification_subscription = User.objects.filter(id=article_author_id).values()[0]['is_subscribed']
        article_slug = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['slug']
        favouriter = request.user.username
        is_favorited = serializer.data['favorited']
        token = JWTAuthentication.encode_token(self, article_username_pk)

        if author_notification_subscription:
            current_site = get_current_site(request)
            link = "http://" + current_site.domain + \
            '/api/notifications/subscription/'+token+'/'
            article_link = "http://" + current_site.domain + \
            '/api/articles/{}/'.format(article_slug)

            from_email = 'codeofd@gmail.com'
            template='favorite.html'
            to = [article_author]
            subject='"{}" favourited your article, "{}"'.format(favouriter, article_title)
            html_content = render_to_string(template, context={
                                            "username": article_username,
                                            "favouriter": favouriter,
                                            'article_title': article_title,
                                            'article_link': article_link,
                                            "unsubscribe_url":link})
            #send Email
            send_mail(subject, '', from_email, to, html_message=html_content)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug=None):
        """
        method to unfavorite an article
        """
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

            article_author_id = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['author_id']
            article_slug = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['slug']
            article_title = Article.objects.filter(slug=self.kwargs["slug"]).values()[0]['title']
            article_author = User.objects.filter(id=article_author_id).values()[0]['username']
            articles_instance = Article.objects.get(slug=article_slug)
            favouriters = articles_instance.favorited_by.values()
            commenter = request.user.username

            for user_id in favouriters:
                favouriters_name = User.objects.get(id=user_id['user_id'])
                token = JWTAuthentication.encode_token(self, favouriters_name.pk)
                author_notification_subscription = User.objects.filter(id=favouriters_name.pk).values()[0]['is_subscribed']

                if author_notification_subscription:
                    current_site = get_current_site(request)
                    link = "http://" + current_site.domain + \
                    '/api/notifications/subscription/'+token+'/'
                    article_link = "http://" + current_site.domain + \
                    '/api/articles/{}/'.format(article_slug)

                    from_email = 'codeofd@gmail.com'
                    template='comments.html'
                    to = [favouriters_name.email]
                    subject='New comment on one of your favorite articles, "{}" by "{}"'.format(article_title, article_author)
                    html_content = render_to_string(template, context={
                                                    "username": favouriters_name.username,
                                                    "commenter": commenter,
                                                    'article_title': article_title,
                                                    'article_link': article_link,
                                                    "unsubscribe_url":link})
                    #send Email
                    send_mail(subject, '', from_email, to, html_message=html_content)
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


class ArticlesFeedAPIView(ListAPIView):
    """
    Returns multiple articles created by followed users, ordered by most recent first.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        following = list(self.request.user.profile.follows.all())
        user = [profile.user for profile in following]

        return Article.objects.filter(
            author__in=user
        )

    def list(self, request):
        queryset = self.get_queryset()

        serializer_context = {'request': request}
        serializer = self.serializer_class(
            queryset, context=serializer_context, many=True
        )

        return Response(serializer.data)


class ArticleFilterAPIView(filters.FilterSet):
    """
    creates a custom filter class for articles
    """
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    description = filters.CharFilter(
        field_name='description', lookup_expr='icontains')
    body = filters.CharFilter(field_name='body', lookup_expr='icontains')
    author__username = filters.CharFilter(
        field_name='author__username', lookup_expr='icontains')

    class Meta:
        """
        This class describes the fields to be used in the search.
        Overrides the ArrayField
        """
        model = Article
        fields = [
            'title', 'description', 'body', 'tags', 'author__username'
        ]
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains', },
            },
        }


class ArticlesSearchListAPIView(ListAPIView):
    """
    Implements search functionality
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    search_list = ['title', 'body', 'description', 'tags', 'author__username']
    filter_list = ['title', 'tags', 'author__username']
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # DjangoFilterBackend class, allows you to easily create filters across relationships,
    # or create multiple filter lookup types for a given field.
    # SearchFilter class supports simple single query parameter based searching
    # It will only be applied if the view has a search_fields attribute set.
    # The search_fields attribute should be a list of names of text type fields on the model,
    # such as CharField or TextField.

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = filter_list
    search_fields = search_list
    filterset_class = ArticleFilterAPIView


class CommentHistoryAPIView(generics.ListAPIView):
    """This class has fetchies comment edit history"""
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


class HighlightCommentView(ArticleMetaData, viewsets.ModelViewSet):
    """
    view allowing highlighting and commenting on a specific part of an article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = HighlightSerializer

    def list(self, request, slug):
        '''get all highlights of an article'''
        article = self.check_article_exists(slug)
        highlights = article.highlights.values()

        return Response(dict(highlights=highlights))

    def post(self, request, slug):
        '''create a new highlight or comment on article'''
        article = self.check_article_exists(slug)
        highlighter = request.user
        serializer = self.serializer_class(data=request.data, context=dict(
            article=article,
            highlighter=highlighter))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug, id):
        '''get a particular text highlight'''
        highlight = get_object_or_404(Highlight, id=id)
        serializer = self.serializer_class(highlight, data=request.data,
                                           context=dict(user=request.user),
                                           partial=True)
        serializer.is_valid()
        return Response(serializer.data)

    def put(self, request, slug, id):
        '''update a particular highlight on an article'''
        highlight = get_object_or_404(Highlight, id=id)
        serializer = self.serializer_class(highlight, data=request.data,
                                           context=dict(user=request.user),
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, id):
        '''delete a particular highlight or comment on an article'''
        self.check_article_exists(slug=slug)
        highlight = get_object_or_404(Highlight, id=id)
        if request.user != highlight.highlighter:
            raise PermissionDenied
        highlight.delete()
        return Response(dict(message="Comment deleted"),
                        status=status.HTTP_200_OK)


class LikeComments(UpdateAPIView):
    """Class for comment likes"""
    serializer_class = CommentSerializer

    def update(self, request, *args, **kwargs):
        """Method for updating comment likes"""
        slug = self.kwargs['slug']
        try:
            Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({'Error': 'The article does not exist'}, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('id')
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            message = {"Error": "A comment with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)
        # fetch user
        user = request.user
        # Confirmation user already liked the comment
        confirm = bool(user in comment.likes.all())
        if confirm is True:
            comment.likes.remove(user.id)
            return Response({"Success": "You un-liked this comment"}, status.HTTP_200_OK)
        # Adding user like to list of likes
        comment.likes.add(user.id)
        message = {"Success": "You liked this comment"}
        return Response(message, status.HTTP_200_OK)


class ReportCreateAPIView(generics.CreateAPIView):
    """Facilitate create reports"""
    slug = 'slug'

    queryset = Report.objects.select_related()
    serializer_class = ReportSerializer
    renderer_classes = (ReportJSONRenderer,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def filter_queryset(self, queryset):
        """Handle getting reports on an article."""
        filters = {self.lookup_field: self.kwargs[self.slug]}
        return queryset.filter(**filters)

    def create(self, request, **kwargs):
        """Create reports to an article"""
        slug = self.kwargs['slug']
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article does not exist")
        serializer_context = {"reporter": request.user, "slug": slug}
        serializer_data = request.data
        serializer = self.serializer_class(data=serializer_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticlesLikesDislikes(GenericAPIView):
    """ Class for creating and deleting article likes/dislikes"""
    queryset = LikesDislikes.objects.all()
    serializer_class = LikesDislikesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, slug):
        # Check if the article exists in the database
        article = Article.objects.get(slug=slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)
        like = request.data.get('likes', None)
        if type(like) == bool:
            # Check if the article belongs to the current user
            if article.author == request.user:
                message = {'Error': 'You cannot like/unlike your own article'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            like_data = {
                'reader': request.user.id,
                'article': article.id,
                'likes': like
            }
            try:
                user_likes = LikesDislikes.objects.get(
                    article=article.id, reader=request.user.id)
                if user_likes:
                    # checking true for stored and  request data
                    if user_likes.likes and like:
                        return Response(
                            {
                                'detail': 'You have already '
                                          'liked this article.'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    # checking false for stored and  request data
                    elif not user_likes.likes and not like:
                        return Response(
                            {
                                'detail': 'You have already '
                                          'disliked this article.'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    # checking true for stored and request data
                    # one is true and the other false
                    elif like and not user_likes.likes:
                        user_likes.likes = True
                        user_likes.save()
                        article.likes.add(request.user)
                        article.dislikes.remove(request.user)
                        article.save()
                        return Response(
                            {
                                'Success': 'You have liked this article.'
                            }, status=status.HTTP_200_OK)
                    else:
                        user_likes.likes = False
                        user_likes.save()
                        article.likes.remove(request.user)
                        article.dislikes.add(request.user)
                        article.save()
                        return Response(
                            {
                                'Success': 'You have disliked this article.'
                            }, status=status.HTTP_200_OK)
            except LikesDislikes.DoesNotExist:
                serializer = self.serializer_class(data=like_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(article=article, reader=request.user)
                # if the request data is true, we update the article
                # with the new data
                if like:
                    article.likes.add(request.user)
                    article.save()
                    return Response(
                        {
                            'Success': 'You have liked this article.'
                        }, status=status.HTTP_201_CREATED)

                # if the request data is false, we update the article
                # with the new data
                else:
                    article.dislikes.add(request.user)
                    article.save()
                    return Response(
                        {
                            'Success': 'You have disliked this article.'
                        }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    'detail': 'Please indicate whether you '
                              'like/dislike this article.'
                }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        # Checking if the article is in the database
        article = Article.objects.get(slug=slug)
        if isinstance(article, dict):
            return Response(article, status=status.HTTP_404_NOT_FOUND)
        try:
            # Check existence of article and user in the db and get the like
            user_like = LikesDislikes.objects.get(
                article=article.id, reader=request.user.id)
            if user_like:
                if user_like.likes:
                    article.likes.remove(request.user)
                    article.save()
                else:
                    article.dislikes.remove(request.user)
                    article.save()
        except LikesDislikes.DoesNotExist:
            return Response(
                {
                    'Error': 'Likes/dislikes not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        user_like.delete()
        return Response(
            {
                'Success': 'Your reaction has been deleted successfully.'
            }, status=status.HTTP_200_OK)


class TagListAPIView(ListAPIView):
    """
    implements taggging
    """
    queryset = Tag.objects.all()
    pagination_class= None
    serializer_class=TagSerializer
    permission_classes=(AllowAny,)

    def list(self,request):
        """
        fetches existing article tags
        """
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(
            {
                'tags': serializer.data
            }, status=status.HTTP_200_OK
        )

class BookMarkArticle(ArticleMetaData, ListAPIView):
    """Implements bookmarking an article"""
    permission_classes = IsAuthenticated,

    def put(self, request, slug):
        """"Method to either bookmark or remove an article from bookmarks"""
        article = self.check_article_exists(slug)
        user = User.objects.get(email=request.user)
        bookmarked_article = user.profile.bookmarks.filter(slug=slug).first()
        if bookmarked_article:
            user.profile.bookmarks.remove(bookmarked_article)
            return Response(dict(message="Article removed from bookmarks!"))
        user.profile.bookmarks.add(article)
        return Response(dict(message="Article bookmarked!"), status=status.HTTP_200_OK)


class BookMarksView(ListAPIView):
    """Class retrieves all user bookmarks"""
    permission_classes = IsAuthenticated,
    serializer_class = ArticleSerializer

    def get(self, request):
        """fetch all a users bookmarks"""
        user = User.objects.get(email=request.user)
        bookmarked_articles = user.profile.bookmarks.all()
        serializer = self.serializer_class(
            bookmarked_articles, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
