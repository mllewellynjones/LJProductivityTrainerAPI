from django.contrib.auth.models import User#
from rest_framework import serializers
from .models import Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['user', 'task_description', 'task_created_datetime', 'task_due_datetime', 'task_status']