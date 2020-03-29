import json
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .helpers import HelperFunctions

TEST_USER_1_INFO = {'username': 'test_user_1', 'password': 'dummypass'}
TEST_USER_2_INFO = {'username': 'test_user_2', 'password': 'dummypass2'}

class UserTestCase(TestCase):

    def setUp(self):

        self.client = Client()

        # Create a couple of test users in the database
        self.user1 = User.objects.create_user(**TEST_USER_1_INFO)
        self.user2 = User.objects.create_user(**TEST_USER_2_INFO)

        # Some data to create a new user when required
        self.new_user_info = {
            'username': 'test_user3',
            'password': 'dummypass3'
        }

    def post_to_users(self, data):
        return self.client.post('/api/users/', data, content_type='application/json')

    def get_from_users(self):
        return self.client.get("/api/users/")

    def post_to_auth(self, data):
        return self.client.post('/auth/', data, content_type='application/json')

    def test_retrieve_existing_user(self):
        response = self.get_from_users()

        self.assertEqual(json.loads(response.content), [
            {'id': 1, 'username': TEST_USER_1_INFO['username']},
            {'id': 2, 'username': TEST_USER_2_INFO['username']},
        ])

    def test_create_new_user(self):
        response = self.post_to_users(self.new_user_info)

        # Expect a 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Message should contain confirmation as well as details of the use
        self.assertEqual(json.loads(response.content), {
            "message": "User created successfully",
            "data": {"id": 3, "username": self.new_user_info['username']}
        })

    def test_fail_duplicate_user(self):
        # Create a new user successfully
        response = self.post_to_users(self.new_user_info)
        self.assertContains(response, "User created successfully", status_code=status.HTTP_200_OK)

        # Try to create the same user again
        # Expect a 400 Bad Request with a message that the user already exists
        response = self.post_to_users(self.new_user_info)
        self.assertContains(response, 'User already exists', status_code=status.HTTP_400_BAD_REQUEST)

    def test_retrieve_authentication_token(self):
        # Send a request for a token with the correct username and password
        data = {'username': TEST_USER_1_INFO['username'], 'password': TEST_USER_1_INFO['password']}
        response = self.post_to_auth(data)

        # Expect a 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the received token corresponds to user 1
        received_token = response.data['token']
        user = Token.objects.get(key=received_token).user
        self.assertEqual(user, self.user1)

    def test_failed_authentication_token(self):
        # Send a request for a token with a valid username but the wrong password
        data = {'username': TEST_USER_1_INFO['username'], 'password': 'XXX'}
        response = self.post_to_auth(data)

        # Expect a 400 that says we could not log in with the provided credentials
        self.assertContains(
            response,
            'Unable to log in with provided credentials',
            status_code=status.HTTP_400_BAD_REQUEST
        )
