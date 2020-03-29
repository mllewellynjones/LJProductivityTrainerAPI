from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class HelperFunctions():

    def __init__(self):
        self.client = Client()

    def create_user_with_token(self, test_user=None, username='', password=''):

        if test_user:
            test_username = 'test_user_' + str(test_user)
            test_password = 'dummypass' + str(test_user)
            user = User.objects.create_user(username=test_username, password=test_password)
            token = Token.objects.create(user=user)

        elif username and password:
            user = User(username=test_username, password=test_password)
            token = Token.objects.create(user=user)

        else:
            user = None
            token = None

        return user, token
