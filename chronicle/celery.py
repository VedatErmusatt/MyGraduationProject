import os

from celery import Celery
from celery.schedules import crontab
from django.utils import timezone

# Django ayarlarını Celery'ye bildir
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chronicle.settings")

app = Celery("chronicle")

# Django ayarlarından Celery yapılandırmasını yükle
app.config_from_object("django.conf:settings", namespace="CELERY")

# Periyodik görevleri yapılandır
app.conf.beat_schedule = {
    "check-appointments": {
        "task": "health_data.tasks.check_appointments",
        "schedule": crontab(minute="*/15"),  # Her 15 dakikada bir kontrol et
    },
    # "check-medication-reminders": {
    #     "task": "health_data.tasks.check_medication_reminders",
    #     # Her 5 dakikada bir çalıştır
    #     "schedule": crontab(minute="*/5"),
    # },
}


# Dinamik zamanlama için özel scheduler
class DynamicScheduler:
    def __init__(self, app):
        self.app = app
        self._schedule = {}
        self._initialized = False

    def setup_schedule(self):
        """Başlangıçta tüm aktif ilaçlar için zamanlayıcıları oluştur"""
        # Django modellerini burada import et
        from health_data.models import Medication
        from health_data.tasks import schedule_next_reminder

        # Tüm aktif ilaçlar için zamanlayıcıları oluştur
        medications = Medication.objects.filter(is_active=True, start_date__lte=timezone.now().date()).exclude(
            end_date__lt=timezone.now().date()
        )

        for medication in medications:
            schedule_next_reminder(medication)

    def get_schedule(self):
        """Mevcut zamanlayıcıları döndür"""
        if not self._initialized:
            self.setup_schedule()
            self._initialized = True
        return self._schedule


# Dinamik zamanlayıcıyı Celery'ye ekle
app.conf.beat_scheduler = DynamicScheduler(app)

# Uygulamalardan görevleri otomatik yükle
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
