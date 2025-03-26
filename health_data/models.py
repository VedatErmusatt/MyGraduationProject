from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class VitalSigns(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vital_signs")
    date = models.DateTimeField(auto_now_add=True)
    blood_pressure_systolic = models.IntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(200)],
        null=True,
        blank=True,
        help_text="Sistolik kan basıncı (mmHg)",
    )
    blood_pressure_diastolic = models.IntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(130)],
        null=True,
        blank=True,
        help_text="Diastolik kan basıncı (mmHg)",
    )
    heart_rate = models.IntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(200)],
        null=True,
        blank=True,
        help_text="Nabız (bpm)",
    )
    temperature = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(35), MaxValueValidator(42)],
        null=True,
        blank=True,
        help_text="Vücut sıcaklığı (°C)",
    )
    blood_sugar = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(2), MaxValueValidator(30)],
        null=True,
        blank=True,
        help_text="Kan şekeri (mmol/L)",
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Vital Bulgu"
        verbose_name_plural = "Vital Bulgular"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%d/%m/%Y %H:%M')}"


class Medication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medications")
    name = models.CharField(max_length=100, help_text="İlaç adı")
    dosage = models.CharField(max_length=50, help_text="Doz")
    frequency = models.CharField(max_length=100, help_text="Kullanım sıklığı")
    start_date = models.DateField(help_text="Başlangıç tarihi")
    end_date = models.DateField(null=True, blank=True, help_text="Bitiş tarihi")
    notes = models.TextField(blank=True)
    reminder_time = models.TimeField(null=True, blank=True, help_text="Hatırlatma saati")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "İlaç"
        verbose_name_plural = "İlaçlar"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Exercise(models.Model):
    EXERCISE_TYPES = (
        ("walking", "Yürüyüş"),
        ("running", "Koşu"),
        ("cycling", "Bisiklet"),
        ("swimming", "Yüzme"),
        ("strength", "Kuvvet Antrenmanı"),
        ("yoga", "Yoga"),
        ("other", "Diğer"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exercises")
    date = models.DateField()
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    duration = models.IntegerField(help_text="Süre (dakika)")
    intensity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Yoğunluk (1-10)",
    )
    calories_burned = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Egzersiz"
        verbose_name_plural = "Egzersizler"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_exercise_type_display()} - {self.user.username} - {self.date}"


class Sleep(models.Model):
    SLEEP_QUALITY_CHOICES = (
        (1, "Çok Kötü"),
        (2, "Kötü"),
        (3, "Orta"),
        (4, "İyi"),
        (5, "Çok İyi"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sleep_records")
    date = models.DateField()
    sleep_time = models.TimeField(help_text="Uyku başlangıç saati")
    wake_time = models.TimeField(help_text="Uyanma saati")
    quality = models.IntegerField(choices=SLEEP_QUALITY_CHOICES)
    duration = models.DecimalField(max_digits=4, decimal_places=1, help_text="Uyku süresi (saat)")
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Uyku Kaydı"
        verbose_name_plural = "Uyku Kayıtları"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"
