from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

User = get_user_model()

# Create your models here.


class Medication(models.Model):
    FREQUENCY_CHOICES = (
        ("daily", "Günde Bir"),
        ("twice_daily", "Günde İki"),
        ("three_times_daily", "Günde Üç"),
        ("four_times_daily", "Günde Dört"),
        ("weekly", "Haftada Bir"),
        ("custom", "Özel"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medications")
    name = models.CharField(max_length=100, help_text="İlaç adı")
    dosage = models.CharField(max_length=50, help_text="Doz")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, help_text="Kullanım sıklığı")
    custom_frequency = models.CharField(
        max_length=100, blank=True, help_text="Özel kullanım sıklığı (örn: Her 8 saatte bir)"
    )
    start_date = models.DateField(help_text="Başlangıç tarihi")
    end_date = models.DateField(null=True, blank=True, help_text="Bitiş tarihi")
    notes = models.TextField(blank=True)
    reminder_times = models.JSONField(default=list, help_text="Hatırlatma saatleri (HH:MM formatında)")
    is_active = models.BooleanField(default=True)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "İlaç"
        verbose_name_plural = "İlaçlar"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def get_next_reminder_time(self):
        """Bir sonraki hatırlatma zamanını hesapla"""
        if not self.reminder_times or not self.is_active:
            return None

        now = timezone.now()
        if self.end_date and now.date() > self.end_date:
            return None

        # Bugünün hatırlatma saatlerini kontrol et
        today_reminders = []
        for reminder_time in self.reminder_times:
            hour, minute = map(int, reminder_time.split(":"))
            reminder_datetime = timezone.make_aware(datetime.combine(now.date(), time(hour, minute)))
            if reminder_datetime > now:
                today_reminders.append(reminder_datetime)

        if today_reminders:
            return min(today_reminders)

        # Bugün için hatırlatma kalmadıysa, yarının ilk hatırlatmasını döndür
        tomorrow = now.date() + timedelta(days=1)
        hour, minute = map(int, self.reminder_times[0].split(":"))
        return timezone.make_aware(datetime.combine(tomorrow, time(hour, minute)))

    def save(self, *args, **kwargs):
        """Model kaydedilirken hatırlatma saatlerini otomatik ayarla ve hatırlatma görevi oluştur"""
        is_new = self.pk is None

        # Hatırlatma saatlerini ayarla
        if self.frequency == "daily" and not self.reminder_times:
            self.reminder_times = ["09:00"]
        elif self.frequency == "twice_daily" and not self.reminder_times:
            self.reminder_times = ["09:00", "21:00"]
        elif self.frequency == "three_times_daily" and not self.reminder_times:
            self.reminder_times = ["09:00", "14:00", "21:00"]
        elif self.frequency == "four_times_daily" and not self.reminder_times:
            self.reminder_times = ["08:00", "12:00", "16:00", "20:00"]
        elif self.frequency == "weekly" and not self.reminder_times:
            self.reminder_times = ["10:00"]

        super().save(*args, **kwargs)

        # İlaç aktifse ve başlangıç tarihi geçmişse hatırlatma görevi oluştur
        if self.is_active and self.start_date <= timezone.now().date():
            from .tasks import schedule_next_reminder

            schedule_next_reminder(self)


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


class Message(models.Model):
    """Doktor-hasta mesajlaşma ve hatırlatma modeli"""

    MESSAGE_TYPES = (
        ("chat", "Sohbet"),
        ("reminder", "Hatırlatma"),
    )

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="health_sent_messages")
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="health_received_messages"
    )
    subject = models.CharField(max_length=200, verbose_name="Konu")
    content = models.TextField(verbose_name="Mesaj")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default="chat", verbose_name="Mesaj Tipi")
    related_medication = models.ForeignKey(
        "Medication", on_delete=models.SET_NULL, null=True, blank=True, related_name="reminder_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    parent_message = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="health_replies"
    )

    class Meta:
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender.get_full_name()} -> {self.receiver.get_full_name()}: {self.subject}"

    def mark_as_read(self):
        """Mesajı okundu olarak işaretle"""
        self.is_read = True
        self.save(update_fields=["is_read"])


class DailyActivity(models.Model):
    """Günlük aktivite takibi (adım sayısı, su tüketimi vb.)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField(auto_now_add=True)
    steps = models.PositiveIntegerField(default=0, verbose_name="Adım Sayısı")
    water_intake = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name="Su Tüketimi (L)")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Günlük Aktivite"
        verbose_name_plural = "Günlük Aktiviteler"
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date}"

    def get_absolute_url(self):
        return reverse('health_data:daily_activity_detail', args=[str(self.id)])


class HealthTip(models.Model):
    """Sağlık ipuçları"""
    title = models.CharField(max_length=200, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', 'Genel'),
            ('exercise', 'Egzersiz'),
            ('nutrition', 'Beslenme'),
            ('sleep', 'Uyku'),
            ('medication', 'İlaç Kullanımı'),
            ('mental', 'Mental Sağlık'),
        ],
        default='general',
        verbose_name="Kategori"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sağlık İpucu"
        verbose_name_plural = "Sağlık İpuçları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Appointment(models.Model):
    """Doktor randevuları"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField(verbose_name="Tarih")
    time = models.TimeField(verbose_name="Saat", default="09:00")
    department = models.CharField(max_length=100, verbose_name="Bölüm", default="Genel")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    notification_sent = models.BooleanField(default=False, verbose_name="Bildirim Gönderildi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Randevu"
        verbose_name_plural = "Randevular"
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_name()} - {self.date} {self.time}"

    def get_absolute_url(self):
        return reverse('health_data:appointment_detail', args=[str(self.id)])


class HospitalRecord(models.Model):
    """Hastane kayıtları için ana model"""

    RECORD_TYPES = [
        ("intervention", _("Müdahale")),
        ("xray", _("Röntgen")),
        ("blood_test", _("Kan Testi")),
        ("lab_test", _("Laboratuvar Testi")),
        ("imaging", _("Görüntüleme")),
        ("treatment", _("Tedavi")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Hasta"))
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, verbose_name=_("Kayıt Tipi"))
    date = models.DateField(verbose_name=_("Tarih"))
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    description = models.TextField(verbose_name=_("Açıklama"))
    results = models.TextField(verbose_name=_("Sonuçlar"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notlar"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Hastane Kaydı")
        verbose_name_plural = _("Hastane Kayıtları")
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_record_type_display()} - {self.date} - {self.title}"


class BloodTestResult(models.Model):
    """Kan testi sonuçları için detay model"""

    hospital_record = models.ForeignKey(HospitalRecord, on_delete=models.CASCADE, related_name="blood_test_results")
    parameter = models.CharField(max_length=100, verbose_name=_("Parametre"))
    value = models.CharField(max_length=50, verbose_name=_("Değer"))
    unit = models.CharField(max_length=20, verbose_name=_("Birim"))
    reference_range = models.CharField(max_length=100, verbose_name=_("Referans Aralığı"))
    is_abnormal = models.BooleanField(default=False, verbose_name=_("Anormal mi?"))

    class Meta:
        verbose_name = _("Kan Testi Sonucu")
        verbose_name_plural = _("Kan Testi Sonuçları")

    def __str__(self):
        return f"{self.parameter}: {self.value} {self.unit}"


class LabTestResult(models.Model):
    """Laboratuvar testi sonuçları için detay model"""

    hospital_record = models.ForeignKey(HospitalRecord, on_delete=models.CASCADE, related_name="lab_test_results")
    test_name = models.CharField(max_length=200, verbose_name=_("Test Adı"))
    result = models.TextField(verbose_name=_("Sonuç"))
    interpretation = models.TextField(verbose_name=_("Yorum"))

    class Meta:
        verbose_name = _("Laboratuvar Testi Sonucu")
        verbose_name_plural = _("Laboratuvar Testi Sonuçları")

    def __str__(self):
        return f"{self.test_name} - {self.hospital_record.date}"
