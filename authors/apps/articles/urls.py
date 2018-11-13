'''articles/urls.py'''
from django.urls import path
from .views import ArticlesView, ArticlesFavoriteAPIView, DislikeComments, LikeComments
from .views import CommentRetrieveUpdateDestroy, CommentsListCreateAPIView

# map http methods to defined methods in ArticlesViews
articles_list = ArticlesView.as_view({
    'get': 'list',
    'post': 'create',

})
articles_detail = ArticlesView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# crud methods
comments_list = CommentRetrieveUpdateDestroy.as_view({
    'delete': 'delete_a_comment',
    'post': 'create_a_reply',
    'put': 'update_a_comment',
    'get': 'fetch_a_comment'
})
# retrieve all and create a comment
comments_details = CommentsListCreateAPIView.as_view({
    'get': 'fetch_all_comments',
    'post': 'create_a_comment'
})

# like a comment
like_comment = LikeComments.as_view()
dislike_comment = DislikeComments.as_view()

urlpatterns = [
    path('articles/', articles_list, name='articles'),
    path('articles/<slug>/', articles_detail, name='article'),
    path('articles/<slug>/favorite', ArticlesFavoriteAPIView.as_view(), name='favorite_article'),
    path('articles/<slug>/comment/<int:id>/', comments_list, name='comment_an_article'),
    path('articles/<slug>/comment/', comments_details, name='modify_a_comment'),
    path('articles/<slug>/comment/<int:id>/like/', like_comment, name='like_comment'),
    path('articles/<slug>/comment/<int:id>/dislike/', dislike_comment, name='dislike_comment'),
]
