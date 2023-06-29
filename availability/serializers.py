from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Availability, RendezVous, Message
from user.serializers import UserSerializer

User = get_user_model()


class AvailabilitySerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%d-%m-%Y")

    class Meta:
        model = Availability
        fields = ['id', 'date', 'heure', 'is_taken']


class RendezVousSerializer(serializers.ModelSerializer):
    availability = serializers.PrimaryKeyRelatedField(
        queryset=Availability.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = RendezVous
        fields = ['id', 'user', 'degree', 'availability']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['availability'] = AvailabilitySerializer(
            instance.availability).data
        representation["user"] = UserSerializer(instance.user).data
        return representation


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'rdv', 'sender', 'content', 'date_time']
        # read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["sender"] = UserSerializer(instance.sender).data
        return representation
