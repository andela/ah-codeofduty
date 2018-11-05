from django.urls import path

from authors.apps.profiles.views import ProfileRetrieveUpdateAPIView

app_name = 'profiles'

urlpatterns = [
    path('<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
]
