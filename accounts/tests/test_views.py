import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

USERNAME = 'username'
EMAIL = 'email@email.com'
PASSWORD = 'secret123password'


def get_errors(response):
    return json.loads(response.content.decode())


class TestChangePassword(APITestCase):

    url = reverse('change_password')

    def setUp(self):
        self.user = User.objects.create_user(USERNAME, password=PASSWORD)
        self.client.force_authenticate(user=self.user)
        self.data = {
            'current_password': PASSWORD,
            'new_password': 'NewPassword1234',
            'new_password_confirm': 'NewPassword1234',
        }

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_unauthorized(self):
        self.client.logout()
        response = self.client.put(self.url, data=self.data)
        self.assertEqual(response.status_code, 401)

    def test_passwords_not_matching(self):
        self.data['new_password_confirm'] = 'NotMatchingPassword1234'
        response = self.client.put(self.url, data=self.data)
        errors = get_errors(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(errors, {'new_password_confirm': ['Password fields didn\'t match']})

    def test_incorrect_password(self):
        self.data['current_password'] = 'WrongPassword1234'
        response = self.client.put(self.url, data=self.data)
        errors = get_errors(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(errors, {'current_password': ['Password is not correct']})

    def test_invalid_password(self):
        self.data['new_password'] = 'password'
        self.data['new_password_confirm'] = 'password'
        response = self.client.put(self.url, data=self.data)
        errors = get_errors(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(errors, {'new_password': ['This password is too common.']})

    def test_updates_password(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.data['new_password']))


class TestLogin(APITestCase):

    url = reverse('login')

    def setUp(self):
        self.user = User.objects.create_user(
            USERNAME,
            email=EMAIL,
            password=PASSWORD
        )
        self.data = {
            'username': USERNAME,
            'password': PASSWORD,
        }

    def test_login_using_username_and_password(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)

    def test_login_using_email_and_password(self):
        self.data['username'] = EMAIL
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)

    def test_login_no_email_or_username(self):
        del self.data['username']
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_login_bad_username(self):
        self.data['username'] = 'badusername'
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)
        errors = get_errors(response)
        self.assertEqual(errors, {'non_field_errors': ['The username or password you entered do not match an account. Please try again.']})

    def test_login_bad_email(self):
        self.data['username'] = 'bademail@fakeemail.com'
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 400)
        errors = get_errors(response)
        self.assertEqual(errors, {'non_field_errors': ['The email or password you entered do not match an account. Please try again.']})
