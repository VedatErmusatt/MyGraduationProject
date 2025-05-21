from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_medication_reminder_email(medication, user):
    """İlaç hatırlatma emaili gönderir."""
    subject = f"İlaç Hatırlatması: {medication.name}"

    # Email template'i için context
    context = {
        "user": user,
        "medication": medication,
        "reminder_times": medication.reminder_times,
    }

    # HTML template'i render et
    html_message = render_to_string("health_data/email/medication_reminder.html", context)
    plain_message = strip_tags(html_message)  # HTML olmayan versiyon

    # Email gönder
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_appointment_reminder_email(appointment):
    """Randevu hatırlatma emaili gönderir."""
    subject = f"Randevu Hatırlatması: {appointment.doctor.get_full_name()}"

    context = {
        "appointment": appointment,
        "patient": appointment.patient,
        "doctor": appointment.doctor,
    }

    html_message = render_to_string("health_data/email/appointment_reminder.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.patient.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_message_notification_email(message):
    """Yeni mesaj bildirimi emaili gönderir."""
    subject = f"Yeni Mesaj: {message.subject}"

    context = {
        "message": message,
        "receiver": message.receiver,
        "sender": message.sender,
    }

    html_message = render_to_string("health_data/email/message_notification.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[message.receiver.email],
        html_message=html_message,
        fail_silently=False,
    )
