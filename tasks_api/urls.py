from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import TaskViewSet

router = routers.DefaultRouter()
router.register('tasks', TaskViewSet, basename="TaskViewSet")

urlpatterns = [
    path('', include(router.urls))
]