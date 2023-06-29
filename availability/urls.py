from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilityViewSet, ReadOnlyAvailabilityViewSet, RendezVousViewSet, MessageViewSet

app_name = "availability"
router = DefaultRouter()
router.register("superuser", AvailabilityViewSet,
                basename='superuser-availability')
router.register("user", ReadOnlyAvailabilityViewSet,
                basename='availability')
router.register("rendezvous", RendezVousViewSet, basename='rendezvous')
router.register("messages", MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
