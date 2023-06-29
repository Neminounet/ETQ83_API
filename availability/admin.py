from django.contrib import admin
from availability.models import Availability, RendezVous, Message


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    ordering = ["date", "heure"]
    list_display = ("date", "heure", "is_taken")


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    ordering = ["availability"]
    list_display = ("user", "availability", "degree")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    ordering = ["date_time"]
    list_display = ("rdv", "sender", "date_time")
