import json
import logging
from datetime import time, timedelta

from celery import shared_task
from django.template.loader import render_to_string
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .models import Appointment, Medication, Message
from .utils import send_medication_reminder_email

# Logger'ı yapılandır
logger = logging.getLogger(__name__)


@shared_task
def check_appointments():
    """Yaklaşan randevuları kontrol et ve bildirim gönder"""
    # Şu andan 24 saat sonrasına kadar olan randevuları kontrol et
    now = timezone.now()
    tomorrow = now + timedelta(days=1)

    # Bildirim gönderilecek randevuları bul
    appointments = Appointment.objects.filter(date__range=[now, tomorrow], notification_sent=False, is_active=True)

    for appointment in appointments:
        # Randevuya kalan süreyi hesapla
        time_until = appointment.date - now
        hours_until = time_until.total_seconds() / 3600

        # Eğer randevuya 24 saat veya daha az kaldıysa bildirim gönder
        if hours_until <= 24:
            send_appointment_notification(appointment)
            appointment.notification_sent = True
            appointment.save()


def send_appointment_notification(appointment):
    """Randevu bildirimi gönder"""
    # Mesaj içeriğini hazırla
    context = {
        "appointment": appointment,
        "patient_name": appointment.patient.get_full_name() or appointment.patient.email,
        "doctor_name": appointment.doctor.get_full_name() or appointment.doctor.email,
        "appointment_date": appointment.date.strftime("%d.%m.%Y %H:%M"),
    }

    # E-posta bildirimi gönder
    subject = f"Randevu Hatırlatması: {appointment.date.strftime('%d.%m.%Y %H:%M')}"
    message = render_to_string("health_data/email/appointment_reminder.html", context)

    # Hastaya bildirim gönder
    # TODO
    # send_mail(
    #     subject=subject,
    #     message=message,
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[appointment.patient.email],
    #     html_message=message,
    #     fail_silently=True,
    # )

    # # Doktora bildirim gönder
    # send_mail(
    #     subject=subject,
    #     message=message,
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[appointment.doctor.email],
    #     html_message=message,
    #     fail_silently=True,
    # )

    # Uygulama içi mesaj gönder
    Message.objects.create(
        sender=appointment.doctor,
        receiver=appointment.patient,
        subject=f"Randevu Hatırlatması: {appointment.date.strftime('%d.%m.%Y %H:%M')}",
        content=f"Sayın {appointment.patient.get_full_name() or appointment.patient.email},\n\n"
        f"{appointment.date.strftime('%d.%m.%Y %H:%M')} tarihindeki randevunuzu hatırlatmak isteriz.\n\n"
        f"Randevu Detayları:\n"
        f"Doktor: {appointment.doctor.get_full_name() or appointment.doctor.email}\n"
        f"Tarih: {appointment.date.strftime('%d.%m.%Y')}\n"
        f"Saat: {appointment.date.strftime('%H:%M')}\n"
        f"Not: {appointment.notes or 'Belirtilmemiş'}\n\n"
        f"Sağlıklı günler dileriz.",
    )


@shared_task
def check_medication_reminders():
    """Aktif ilaçlar için hatırlatma kontrolü yapar ve gerekirse email gönderir."""
    now = timezone.now()
    current_time = now.time()
    current_date = now.date()

    # Aktif ilaçları al
    active_medications = Medication.objects.filter(
        is_active=True,
        start_date__lte=current_date,
        end_date__gte=current_date,
    )

    for medication in active_medications:
        # İlacın hatırlatma saatlerini kontrol et
        for reminder_time_str in medication.reminder_times:
            try:
                # String formatındaki saati datetime.time objesine çevir
                hour, minute = map(int, reminder_time_str.split(":"))
                reminder_time = time(hour, minute)

                # Eğer şu anki saat, hatırlatma saatine yakınsa (5 dakika tolerans)
                if (
                    abs(
                        (current_time.hour * 60 + current_time.minute)
                        - (reminder_time.hour * 60 + reminder_time.minute)
                    )
                    <= 5
                ):
                    # Email gönder
                    send_medication_reminder_email(medication, medication.user)
            except (ValueError, TypeError):
                # Geçersiz saat formatı, bu saati atla
                continue


@shared_task
def send_medication_reminder(medication_id):
    """İlaç hatırlatması gönder"""
    try:
        medication = Medication.objects.get(id=medication_id)
        if not medication.is_active:
            logger.info(f"İlaç aktif değil, hatırlatma gönderilmedi: {medication.name} (ID: {medication_id})")
            return

        # Hatırlatma mesajı oluştur
        message = Message.objects.create(
            sender=medication.user,  # Sistem mesajı olarak kullanıcının kendisinden geliyor gibi göster
            receiver=medication.user,
            subject=f"İlaç Hatırlatması: {medication.name}",
            content=f"{medication.name} ilacınızı almanın zamanı geldi.\n"
            f"Doz: {medication.dosage}\n"
            f"Kullanım Sıklığı: {medication.get_frequency_display()}\n"
            f"Notlar: {medication.notes or 'Belirtilmemiş'}",
            message_type="reminder",
            related_medication=medication,
        )
        logger.info(f"İlaç hatırlatma mesajı oluşturuldu: {medication.name} (ID: {medication_id})")

        # Email bildirimi gönder
        try:
            send_medication_reminder_email(medication, medication.user)
            logger.info(
                f"İlaç hatırlatma emaili başarıyla gönderildi: {medication.name} "
                f"(Kullanıcı: {medication.user.email}, ID: {medication_id})"
            )
        except Exception as e:
            logger.error(
                f"İlaç hatırlatma emaili gönderilemedi: {medication.name} "
                f"(Kullanıcı: {medication.user.email}, ID: {medication_id}, Hata: {str(e)})",
                exc_info=True,
            )

        # Bir sonraki hatırlatma için görev oluştur
        schedule_next_reminder(medication)
        logger.info(f"Bir sonraki hatırlatma zamanlandı: {medication.name} (ID: {medication_id})")

    except Medication.DoesNotExist:
        logger.error(f"İlaç bulunamadı: ID {medication_id}")
    except Exception as e:
        logger.error(
            f"İlaç hatırlatma görevi çalıştırılırken hata oluştu: ID {medication_id}, Hata: {str(e)}", exc_info=True
        )


def schedule_next_reminder(medication):
    """Bir sonraki hatırlatma için Celery Beat görevi oluştur"""
    next_reminder = medication.get_next_reminder_time()
    if not next_reminder:
        return

    # Mevcut görevi sil
    task_name = f"medication_reminder_{medication.id}"
    PeriodicTask.objects.filter(name=task_name).delete()

    # Yeni görev için zamanlama oluştur
    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour=next_reminder.hour,
        minute=next_reminder.minute,
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone=timezone.get_current_timezone_name(),
    )

    # Yeni görevi oluştur
    PeriodicTask.objects.create(
        name=task_name,
        task="health_data.tasks.send_medication_reminder",
        crontab=schedule,
        args=json.dumps([medication.id]),
        enabled=True,
        one_off=True,  # Görev sadece bir kez çalışsın
        expires=next_reminder + timedelta(minutes=5),  # 5 dakika sonra görevi iptal et
    )

    # Celery Beat'i yeniden yükle
    from django.core.cache import cache

    cache.delete("django_celery_beat_schedule")
