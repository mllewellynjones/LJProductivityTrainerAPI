from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Task
from django.contrib.auth.models import User
from .serializers import TaskSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        username = request.data['username']
        password = request.data['password']
        try:
            user = User.objects.create_user(username=username, password=password)
            serializer = UserSerializer(user, many=False)
            response = {'message': 'User created successfully', 'data': serializer.data}
            return Response(response, status=status.HTTP_200_OK)
        except IntegrityError:
            response = {'message': 'User already exists'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Task.objects.all().filter(user=self.request.user)
        return queryset

    def create(self, request):
        task_description = request.data['task_description']
        task_status = request.data['task_status']

        user = self.request.user
        task = Task.objects.create(user=user, task_description=task_description, task_status=task_status)
        serializer = TaskSerializer(task, many=False)
        response = {'message': 'Task created', 'result': serializer.data}
        return Response(response, status=status.HTTP_200_OK)
