import json
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class UserTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        # Create a couple of test users in the database
        self.test_user_1_info = {'username': "test_user", 'password': "dummypass"}
        self.test_user_2_info = {'username': "test_user2", 'password': "dummypass2"}

        self.User1 = User.objects.create_user(**self.test_user_1_info)
        self.User2 = User.objects.create_user(**self.test_user_2_info)

        # Same data to create a new user when required
        self.new_user_info = {
            'username': 'test_user3',
            'password': 'dummypass3'
        }

    def test_retrieve_existing_user(self):
        response = self.client.get("/api/users/")
        self.assertEqual(json.loads(response.content), [
            {'id': 1, 'username': self.test_user_1_info['username']},
            {'id': 2, 'username': self.test_user_2_info['username']},
        ])

    def test_create_new_user(self):
        response = self.client.post(
            '/api/users/',
            self.new_user_info,
            content_type='application/json',
        )

        # Expect a 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Message should contain confirmation as well as details of the use
        self.assertEqual(json.loads(response.content),
                         {"message": "User created successfully", "data": {"id": 3, "username": "test_user3"}}
                         )

    def test_fail_duplicate_user(self):
        response1 = self.client.post(
            '/api/users/',
            self.new_user_info,
            content_type='application/json',
        )
        response2 = self.client.post(
            '/api/users/',
            self.new_user_info,
            content_type='application/json',
        )

        # Expect a 400 Bad Request with a message that the user already exists
        self.assertContains(response2, 'User already exists', status_code=status.HTTP_400_BAD_REQUEST)

    def test_retrieve_authentication_token(self):
        # Send a request for a token with the correct username and password
        response = self.client.post(
            '/auth/',
            {'username': self.test_user_1_info['username'], 'password': self.test_user_1_info['password']},
            content_type='application/json',
        )

        # Expect a 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the received token corresponds to user 1
        received_token = response.data['token']
        user = Token.objects.get(key=received_token).user
        self.assertEqual(user, self.User1)

    def test_failed_authentication_token(self):
        # Send a request for a token with a valid username but the wrong password
        response = self.client.post(
            '/auth/',
            {'username': self.test_user_1_info['username'], 'password': 'XXX'},
            content_type='application/json',
        )

        # Expect a 400 that says we could not log in with the provided credentials
        self.assertContains(
            response,
            'Unable to log in with provided credentials',
            status_code=status.HTTP_400_BAD_REQUEST
        )