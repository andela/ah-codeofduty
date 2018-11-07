'''articles/urls.py'''
from django.urls import path

from .views import ArticlesView

<<<<<<< HEAD
# map http methods to defined methods in ArticlesViews
=======
>>>>>>> Feature(Create Articles): CRUD for Articles
articles_list =  ArticlesView.as_view({
    'get': 'list',
    'post': 'create',

})
articles_detail =  ArticlesView.as_view({
    'get': 'retrieve',
    'put': 'update',
<<<<<<< HEAD
    'delete': 'destroy'
})
urlpatterns = [
    path('articles/', articles_list),
    path('articles/<slug>/', articles_detail)
=======
>>>>>>> Feature(Create Articles): CRUD for Articles
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('articles/', articles_list),
<<<<<<< HEAD
<<<<<<< HEAD
    path('articles/<slug>/', articles_detail)
=======
    path('articles/<id>', articles_detail)
>>>>>>> Feature(Create Articles): CRUD for Articles
=======
    path('articles/<slug>/', articles_detail)
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
]
