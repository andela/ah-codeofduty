from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, VerifyAPIView, UserForgotPassword, UserResetPassword
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('users/verify/<token>/', VerifyAPIView.as_view()),
    path('users/forgot-password/', UserForgotPassword.as_view()),
    path('users/reset-password/<token>/', UserResetPassword.as_view()),
]
