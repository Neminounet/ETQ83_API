from django.contrib.auth import get_user_model
from django.db import transaction
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, authentication, viewsets
from availability.serializers import AvailabilitySerializer, RendezVousSerializer, MessageSerializer
from availability.models import Availability, RendezVous, Message

User = get_user_model()


class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# Rend possible la recherche par paramètres : (django-filters) => exemple : GET /api/rendezvous/?availability_id=1
# --------------------------------------------------


class RendezVousFilter(django_filters.FilterSet):
    availability_id = django_filters.NumberFilter(
        field_name="availability__id")

    class Meta:
        model = RendezVous
        fields = ["availability_id"]


class MessagesFilter(django_filters.FilterSet):
    rdv_id = django_filters.NumberFilter(
        field_name="rdv__id")

    class Meta:
        model = Message
        fields = ["rdv_id"]


#  Disponibilités : CRUD pour superuser :
# =========================

class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    authentication_classes = [authentication.TokenAuthentication]

    queryset = Availability.objects.all()


# Disponibilités : Consultation pour utilisateur non superuser :
# =============================================


class ReadOnlyAvailabilityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Availability.objects.all()

# Rendez-Vous : ModelViewSet
# ==============================


class RendezVousViewSet(viewsets.ModelViewSet):
    serializer_class = RendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RendezVousFilter

    def get_queryset(self):
        user = self.request.user
        queryset = RendezVous.objects.all()

        if self.request.method == "GET":
            filters = RendezVousFilter(self.request.GET, queryset=queryset)
            return filters.qs

        if user.is_superuser:
            return RendezVous.objects.all()
        else:
            return RendezVous.objects.filter(user=user)

    def perform_create(self, serializer):
        with transaction.atomic():
            rdv = serializer.save()
            rdv.availability.is_taken = True
            rdv.availability.save()

# Messages : ModelViewSet
# ==============================


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessagesFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.all()

        if self.request.method == "GET":
            filters = MessagesFilter(self.request.GET, queryset=queryset)
            return filters.qs

        if user.is_superuser:
            return Message.objects.all()
        else:
            return Message.objects.filter(rdv__user=user)
