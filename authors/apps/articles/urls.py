'''articles/urls.py'''
from django.urls import path

from .views import ArticlesView
from .views import CommentRetrieveUpdateDestroy, CommentsListCreateAPIView


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

urlpatterns = [
    path('articles/', articles_list),
    path('articles/<slug>/', articles_detail),
    path('articles/<slug>/comment/<id>',
         CommentRetrieveUpdateDestroy.as_view(), name='a-comment'),
    path('articles/<slug>/comment',
         CommentsListCreateAPIView.as_view(), name='comments')
]
