from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['user', 'task_description', 'task_created_datetime', 'task_due_datetime', 'task_status']

