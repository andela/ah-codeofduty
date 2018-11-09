from django.urls import path

from .views import ProfileRetrieveUpdateAPIView,  ProfileList

app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('profiles/', ProfileList.as_view(), name='profiles'),
]
