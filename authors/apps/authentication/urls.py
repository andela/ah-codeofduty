from django.urls import path

from .views import (
<<<<<<< HEAD
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, VerifyAPIView, UserForgotPassword, UserResetPassword
=======
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, UserForgotPassword, UserResetPassword
>>>>>>> Feauture(Reset Password): Add Reset Password Endpoint
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
<<<<<<< HEAD
    path('users/verify/<token>/', VerifyAPIView.as_view()),
    path('users/forgot-password/', UserForgotPassword.as_view(), name='password_reset'),
    path('users/reset-password/<token>/', UserResetPassword.as_view(), name='password_reset_done'),
=======
    path('users/forgot-password/', UserForgotPassword.as_view(), name='password_reset'),
    path('users/reset-password/<token>/<email>', UserResetPassword.as_view(), name='password_reset_done'),
>>>>>>> Feauture(Reset Password): Add Reset Password Endpoint
]
