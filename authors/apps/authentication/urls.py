from django.conf.urls import url

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

urlpatterns = [
    url('user/', UserRetrieveUpdateAPIView.as_view()),
    url('users/', RegistrationAPIView.as_view()),
    url('users/login/', LoginAPIView.as_view()),
]
