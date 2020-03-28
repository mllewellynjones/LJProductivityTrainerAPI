from django.db import models
from django.contrib.auth import get_user_model

class Task(models.Model):
    """The most basic unit in the app, a single task"""
    ACTIVE = 'ACT'
    HOLD = 'HOL'
    COMPLETED = 'COM'

    STATUS_OPTIONS = [
        (ACTIVE, 'Active'),
        (HOLD, 'On hold'),
        (COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task_description = models.CharField(max_length=120)
    task_created_datetime = models.DateTimeField(auto_now_add=True)
    task_due_datetime = models.DateTimeField(blank=True, null=True)
    task_status = models.CharField(max_length=3, choices=STATUS_OPTIONS, default=ACTIVE)

    def __str__(self):
        return self.task_description