from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='project')


urlpatterns = [
    path('', include(router.urls)),
]
