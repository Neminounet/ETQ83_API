from django.db import models
from django.contrib.auth import get_user_model

# User = get_user_model()


class Availability(models.Model):
    date = models.DateField()
    heure = models.TimeField()
    is_taken = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Disponibilité"
        verbose_name_plural = "Disponibilités"
        ordering = ["date", "heure"]

    def __str__(self):
        return f"{self.date} à {self.heure}"


class RendezVous(models.Model):
    user = models.ForeignKey(
        "user.CustomUser", on_delete=models.CASCADE, verbose_name="Etudiant"
    )
    degree = models.CharField(
        blank=False, max_length=255, default="", verbose_name="Classe"
    )
    availability = models.ForeignKey(
        Availability, on_delete=models.CASCADE
    )
    # price = models.PositiveIntegerField(verbose_name="Prix")

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ["availability"]

    def __str__(self):
        return f"Rendez-vous pour {self.user} le {self.availability.date} à {self.availability.heure} pour un cours de niveau {self.degree}"


class Message(models.Model):
    rdv = models.ForeignKey(RendezVous, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        "user.CustomUser", on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    date_time = models.DateTimeField()

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["date_time"]

    def __str__(self):
        if self.sender is None:
            sender_name = "Inconnu"
        else:
            sender_name = f"{self.sender.first_name} {self.sender.last_name}"

        return f"{self.rdv.availability.date} {self.rdv.availability.heure} /{sender_name} - {self.date_time}"
