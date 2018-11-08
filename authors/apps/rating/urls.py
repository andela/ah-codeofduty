"""
Rating URLS module
"""
from django.urls import path

from rest_framework_swagger.views import get_swagger_view

from .views import RateArticleView

schema_view = get_swagger_view(title="Rate Articles")

article_rating = RateArticleView.as_view({
    'post': 'create',
})

urlpatterns = [
    path('articles/<slug>/rate/', article_rating),
]
