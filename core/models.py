from django.conf import settings
from django.db import models

# Create your models here.


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("appointment", "Randevu"),
        ("medication", "İlaç Hatırlatıcı"),
        ("message", "Mesaj"),
        ("system", "Sistem"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class HealthTip(models.Model):
    CATEGORY_CHOICES = (
        ("general", "Genel Sağlık"),
        ("nutrition", "Beslenme"),
        ("exercise", "Egzersiz"),
        ("mental", "Mental Sağlık"),
        ("sleep", "Uyku"),
        ("chronic", "Kronik Hastalıklar"),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="health_tips/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sağlık İpucu"
        verbose_name_plural = "Sağlık İpuçları"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class EmergencyContact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Acil Durum Kontağı"
        verbose_name_plural = "Acil Durum Kontakları"

    def __str__(self):
        return f"{self.name} - {self.user.username}"
