from django.urls import path

from authors.apps.profiles.views import ProfileRetrieveUpdateAPIView, ListAPIView

app_name = 'profiles'

urlpatterns = [
    path('<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('', ListAPIView.as_view(), name='profiles'),
]