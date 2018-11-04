from django.urls import path

from .views import ProfileRetrieveUpdateAPIView,  ProfileList

app_name = 'profiles'

urlpatterns = [
    path('<username>', ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('', ProfileList.as_view(), name='profiles'),
]
