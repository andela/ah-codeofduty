"""
User notifications articles test module
"""

import json

from rest_framework.views import status

from .base import BaseTest


class UserNotificationsTestCase(BaseTest):
    """
    User notifications test class
    :params: BaseTest:
      the base test class
    """

    def test_get_all_notifications(self):
        """
        test get all user notifications
        """
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(json.loads(response.content)))

    def test_get_all_notifications_unauth(self):
        """
        test get all user notifications
        """
        response = self.client.get(
            self.ALL_NOTIFICATIONS)
        message = json.loads(response.content.decode("utf-8"))['message']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(message, 'you are not subscribed to notifications')


    def test_mark_notification_as_read(self):
        """
        test mark a notification as read
        """
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_notification = json.loads(response.content)[0]['id']
        response = self.client.put(
            self.MARK_AS_READ.format(first_notification),
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            'Notification has been read',
            json.loads(response.content)['message'])

    def test_get_all_read_notifications(self):
        """
        test get all notifications
        """
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_notification = json.loads(response.content)[0]['id']
        second_notification = json.loads(response.content)[1]['id']
        self.client.put(
            self.MARK_AS_READ.format(first_notification),
            HTTP_AUTHORIZATION=self.token)
        self.client.put(
            self.MARK_AS_READ.format(second_notification),
            HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            self.ALL_READ,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(2, len(json.loads(response.content)))


    def test_get_all_unread_notifications (self):
        """
        test get all unread notifications
        """
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_notification = json.loads(response.content)[0]['id']
        self.client.put(
            self.MARK_AS_READ.format(first_notification),
            HTTP_AUTHORIZATION=self.token)
        response = self.client.get(
            self.ALL_UNREAD,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(2, len(json.loads(response.content)))

    def test_user_subscription(self):
        """
        test user subscription
        """
        response = self.client.post(
            self.SUBSCRIPTION,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            'You have successfully unsubscribed from notifications',
            json.loads(response.content)['message'])
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual('you are not subscribed to notifications',
        # json.loads(response.content)['message'])
        response = self.client.post(
            self.SUBSCRIPTION,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            'You have successfully subscribed to notifications',
            json.loads(response.content)['message'])
        response = self.client.get(
            self.ALL_NOTIFICATIONS,
            HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(json.loads(response.content)))

    def test_subscription_via_email(self):
        """
        test subscribe user via email
        """
        token = self.token.split()
        response = self.client.post(
            self.EMAIL_SUBSCRIPTION.format(token[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            'Successfully Unsubscribed from email notifications',
            json.loads(response.content)['message'])
        response = self.client.post(
            self.EMAIL_SUBSCRIPTION.format(token[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            'Successfully Subscribed to email notifications',
            json.loads(response.content)['message'])
