from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import TaskViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('tasks', TaskViewSet, basename="Tasks")
router.register('users', UserViewSet, basename="Users")

urlpatterns = [
    path('', include(router.urls))
]