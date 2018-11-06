'''articles/urls.py'''
from django.urls import path

from .views import ArticlesView

# map http methods to defined methods in ArticlesViews
articles_list =  ArticlesView.as_view({
    'get': 'list',
    'post': 'create',

})
articles_detail =  ArticlesView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})
urlpatterns = [
    path('articles/', articles_list),
    path('articles/<slug>/', articles_detail)
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('articles/', articles_list),
    path('articles/<id>', articles_detail)
]
