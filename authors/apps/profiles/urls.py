from django.urls import path
from .views import ProfileRetrieveUpdateAPIView,  ProfileList, ProfileFollowAPIView, FollowersAPIView, FollowingAPIView


app_name = 'profiles'

urlpatterns = [
    path('profiles/', ProfileList.as_view(), name='profiles'),
    path('profiles/<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('profiles/<username>/follow', ProfileFollowAPIView.as_view(), name='follow'),
    path('profiles/<username>/followers', FollowersAPIView.as_view(), name='followers'),
    path('profiles/<username>/following', FollowingAPIView.as_view(), name='following'),
]
