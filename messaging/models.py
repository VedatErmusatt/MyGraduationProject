from django.conf import settings
from django.db import models

# Create your models here.


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Beklemede"),
        ("confirmed", "Onaylandı"),
        ("cancelled", "İptal Edildi"),
        ("completed", "Tamamlandı"),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Randevu"
        verbose_name_plural = "Randevular"
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} - {self.date} {self.time}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Prescription(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_prescriptions",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_prescriptions",
    )
    date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField(help_text="Teşhis")
    medications = models.TextField(help_text="İlaçlar ve kullanım talimatları")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Reçete"
        verbose_name_plural = "Reçeteler"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} - {self.date}"
