import json
from datetime import datetime
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from tasks_api.models import Task
from .helpers import HelperFunctions
import pytz
from freezegun import freeze_time


class TaskTestCase(TestCase):


    def setUp(self):

        self.maxDiff = None
        self.helper = HelperFunctions()

        # Create a couple of test users in the database
        self.user1, self.user1_token = self.helper.create_user_with_token(1)
        self.user2, self.user2_token = self.helper.create_user_with_token(2)

        # And associated clients; unauthenticated and authenticated
        self.unauthenticated_client = Client()
        self.authenticated_client_1 = Client(HTTP_AUTHORIZATION='Token {}'.format(self.user1_token))

    def post_to_tasks(self, data, authenticated=False):
        if authenticated:
            return self.authenticated_client_1.post('/api/tasks/', data, content_type='application/json')
        else:
            return self.unauthenticated_client.post('/api/tasks/', data, content_type='application/json')

    def get_from_tasks(self, authenticated=False):
        if authenticated:
            return self.authenticated_client_1.get('/api/tasks/', content_type='application/json')
        else:
            return self.unauthenticated_client.get('/api/tasks/', content_type='application/json')


    def test_add_new_task_no_authentication(self):
        # Send a valid request to create a new task, but without an Authorization header
        data = {
            'task_description': 'Test task 2',
            'task_due_datetime': datetime(year=2020, month=3, day=30, hour=9, minute=0),
            'task_status': 'AC',
        }
        response = self.post_to_tasks(data)

        # Expect a 401 Unauthorized with a message that authentication credentials were not provided
        self.assertContains(response,
                            "Authentication credentials were not provided",
                            status_code=status.HTTP_401_UNAUTHORIZED)


    def test_add_new_task_with_authentication(self):
        # Send a valid request to create a new task, with a valid authorization header
        data = {
            'task_description': 'Test task 2',
            'task_due_datetime': datetime(year=2020, month=3, day=30, hour=9, minute=0),
            'task_status': 'AC',
        }
        response = self.post_to_tasks(data, authenticated=True)

        # Expect a 200 OK with confirmation that the task was created successfully
        self.assertContains(response, "Task created successfully", status_code=status.HTTP_200_OK)

        # Make sure the task is in the database
        response = self.get_from_tasks(authenticated=True)
        self.assertContains(response, "Test task 2", status_code=status.HTTP_200_OK)


    def test_add_duplicate_task(self):
        # Send a valid request to create a duplicate task
        data = {
            'task_description': 'Test task 1',
            'task_due_datetime': datetime(year=2020, month=2, day=13, hour=14, minute=21),
            'task_status': 'AC',
        }
        self.post_to_tasks(data, authenticated=True)
        response = self.post_to_tasks(data, authenticated=True)

        # Expect a 200 OK with confirmation that the task was created successfully
        self.assertContains(response, "Task created successfully", status_code=status.HTTP_200_OK)


    def test_retrieve_all_tasks_no_authentication(self):
        # Send a request to retrieve all tasks currently in the database, but without valid authentication
        response = self.get_from_tasks()

        self.assertContains(response,
                            "Authentication credentials were not provided",
                            status_code=status.HTTP_401_UNAUTHORIZED)

    @freeze_time("2020-03-30")
    def test_retrieve_all_tasks_with_authentication(self):
        # Send a request to retrieve all tasks currently in the database with valid authentication
        # Create a dummy task for each user
        task_1_data = {
            'task_description': 'Test task 1',
            'task_due_datetime': None,
            'task_status': 'AC',
        }

        task_2_data = {
            'task_description': 'Test task 2',
            'task_due_datetime': None,
            'task_status': 'AC',
        }

        self.task1 = Task.objects.create(user=self.user1, **task_1_data)
        self.task2 = Task.objects.create(user=self.user2, **task_2_data)

        response = self.get_from_tasks(authenticated=True)

        # Expect a 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # With information about the one task currently in the database for the authenticated user only
        self.assertEqual(len(json.loads(response.content)), 1)
        self.assertDictEqual(json.loads(response.content)[0], {
            "user": 1,
            "task_description": "Test task 1",
            "task_created_datetime": '2020-03-30T00:00:00Z',
            "task_due_datetime": None,
            "task_status": 'AC',
        })