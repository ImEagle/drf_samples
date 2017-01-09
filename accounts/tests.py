# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


class AccountRegisterApiViewTestCase(APITestCase):
    url_register = reverse('accounts:register')
    url_register_step_2 = reverse('accounts:register_step_2')

    def test_unique_user(self):
        username = 'ExampleUser'

        User.objects.create_user(
            username,
            'foobar@example.com',
            first_name='ExampleFirstName',
            last_name='ExampleLastName'
        )

        account_data = {
            'username': username,
            'password': 'foobarpassword',
            'first_name': 'Foo',
            'last_name': 'Bar'
        }

        response = self.client.post(self.url_register, account_data)
        self.assertEqual(400, response.status_code)

        first_user_unmodified = User.objects.get_by_natural_key(username)
        self.assertEqual('foobar@example.com', first_user_unmodified.email)
        self.assertEqual('ExampleFirstName', first_user_unmodified.first_name)
        self.assertEqual('ExampleLastName', first_user_unmodified.last_name)

        response_json = response.json()
        self.assertIn('username', response_json)
        self.assertIn('This field must be unique.', response_json['username'])

    def test_session_token(self):
        account_data = {
            'username': 'FooBarUser',
            'password': 'ExampleFooBar'
        }

        response = self.client.post(self.url_register, account_data)
        self.assertIn('sessionid', response.cookies)
        self.assertEqual(202, response.status_code)

    def test_invalid_user_profile_data(self):
        account_data = {
            'username': 'FooBarUser',
            'password': 'ExampleFooBar'
        }

        response = self.client.post(self.url_register, account_data)
        self.assertEqual(202, response.status_code)

        user_profile_data = {
            'b_date': '2000-01-01',
            'country': 'Poland',
            'home_town': 'Warszawa',
            'post_code': '123-456',
            'telephone_number': '+48123456789',
        }

        self.client.cookies = response.cookies
        response = self.client.post(self.url_register_step_2, user_profile_data)

        self.assertEqual(400, response.status_code)

        response_json = response.json()
        self.assertIn('This field is required.', response_json['birth_date'])
        self.assertIn('This field is required.', response_json['city'])

    def test_missing_session_id(self):
        user_profile_data = {
            'birth_date': '2000-01-01',
            'country': 'Poland',
            'city': 'Warszawa',
            'post_code': '123-456',
            'telephone_number': '+48123456789',
        }

        response = self.client.post(self.url_register_step_2, user_profile_data)

        self.assertEqual(403, response.status_code)

    def test_missing_fields(self):
        account_data = {
            'username': 'example_user',
            'pass': 'foobar',
            'first_name': 'Foo',
            'last_name': 'Bar',
        }

        response = self.client.post(self.url_register, account_data)
        self.assertEqual(400, response.status_code)

    def test_registered_meantime(self):
        account_data = {
            'username': 'FooBarUser',
            'password': 'example'
        }

        response = self.client.post(self.url_register, account_data)
        self.assertEqual(202, response.status_code)

        user_profile_data = {
            'birth_date': '2000-01-01',
            'country': 'Poland',
            'city': 'Warszawa',
            'post_code': '123-456',
            'telephone_number': '+48123456789',
        }

        User.objects.create_user(
            username='FooBarUser',
            password='ExaplePassword'
        )

        self.client.cookies = response.cookies
        response_step = self.client.post(self.url_register_step_2, user_profile_data)

        self.assertEqual(400, response_step.status_code)

        response_json = response_step.json()
        self.assertIn('This field must be unique.', response_json['username'])
        self.assertEqual('', response_step.cookies['sessionid'].value)

    def test_register_full(self):
        account_data = {
            'username': 'FooBarUser',
            'password': 'example'
        }

        response = self.client.post(self.url_register, account_data)
        self.assertEqual(202, response.status_code)

        user_profile_data = {
            'birth_date': '2000-01-01',
            'country': 'Poland',
            'city': 'Warszawa',
            'post_code': '123-456',
            'telephone_number': '+48123456789',
        }

        self.client.cookies = response.cookies
        response_step = self.client.post(self.url_register_step_2, user_profile_data)

        self.assertEqual(200, response_step.status_code)

        response_json = response_step.json()
        self.assertIn('id', response_json)
        self.assertEqual(account_data['username'], response_json['username'])
        self.assertEqual('', response_json['email'])
        self.assertEqual(user_profile_data, response_json['user_profile'])


class AccountAuthenticationApiViewTestCase(APITestCase):
    url = reverse('accounts:login')

    def test_invalid_user(self):
        user_data = {
            'username': 'foo_',
            'password': 'example_password'
        }

        response = self.client.post(self.url, user_data)
        self.assertEqual(401, response.status_code)
        self.assertNotIn('sessionid', response.cookies)

    def test_invalid_password(self):
        User.objects.create_user('FooBarUser', password='examplepassword')

        user_data = {
            'username': 'FooBarUser',
            'password': 'invalid_password'
        }

        response = self.client.post(self.url, user_data)
        self.assertEqual(401, response.status_code)
        self.assertNotIn('sessionid', response.cookies)

    def test_invalid_username(self):
        User.objects.create_user('FooBarUser1', password='examplepassword')

        user_data = {
            'username': 'FooBarUser',
            'password': 'examplepassword'
        }

        response = self.client.post(self.url, user_data)
        self.assertEqual(401, response.status_code)
        self.assertNotIn('sessionid', response.cookies)

    def test_successful_login(self):
        User.objects.create_user('example', password='example_pass')

        user_data = {
            'username': 'example',
            'password': 'example_pass'
        }

        response = self.client.post(self.url, user_data)
        self.assertEqual(200, response.status_code)
        self.assertIn('sessionid', response.cookies)
