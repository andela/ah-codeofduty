from django.urls import path

from .views import ProfileRetrieveUpdateAPIView, ProfileList, ProfileFollowAPIView, FollowersAPIView, FollowingAPIView

app_name = 'profiles'

urlpatterns = [
    path('<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('', ProfileList.as_view(), name='profiles'),
    path('<username>/follow', ProfileFollowAPIView.as_view(), name='follow'),
    path('<username>/followers', FollowersAPIView.as_view(), name='followers'),
    path('<username>/following', FollowingAPIView.as_view(), name='following'),



]
