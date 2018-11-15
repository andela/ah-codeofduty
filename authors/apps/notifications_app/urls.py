from django.urls import path

from .views import (
    UserAllNotificationsView,
    UserReadNotifications,
    UserUnReadNotifications,
    Subscription,
    ReadNotifications,
    SubscriptionEmailAPIView)


urlpatterns = [
    path('notifications/', UserAllNotificationsView.as_view()),
    path('notifications/read/', UserReadNotifications.as_view()),
    path('notifications/unread/', UserUnReadNotifications.as_view()),
    path('notifications/subscription/', Subscription.as_view()),
    path('notifications/subscription/<str:token>/', SubscriptionEmailAPIView.as_view()),
    path('notifications/read_notification/<int:pk>/', ReadNotifications.as_view(), name='read_notifications')
]





