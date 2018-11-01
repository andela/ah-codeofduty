from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, UserForgotPassword, UserResetPassword
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('users/forgot-password/', UserForgotPassword.as_view(), name='password_reset'),
    path('users/reset-password/<token>/', UserResetPassword.as_view(), name='password_reset_done'),
]
