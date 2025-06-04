# Register your models here.

from django.contrib import admin
from django.utils.html import format_html

from .models import Appointment, Exercise, Medication, Message, Sleep


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "receiver", "message_type", "created_at", "is_read", "get_related_medication")
    list_filter = ("message_type", "is_read", "created_at", "sender", "receiver")
    search_fields = ("subject", "content", "sender__email", "receiver__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def get_related_medication(self, obj):
        if obj.related_medication:
            return format_html(
                '<a href="{}">{}</a>',
                f"/admin/health_data/medication/{obj.related_medication.id}/change/",
                obj.related_medication.name,
            )
        return "-"

    get_related_medication.short_description = "İlgili İlaç"


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "frequency", "start_date", "end_date", "is_active")
    list_filter = ("frequency", "is_active", "start_date", "end_date")
    search_fields = ("name", "user__email", "notes")
    date_hierarchy = "start_date"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "is_active", "notification_sent")
    list_filter = ("is_active", "notification_sent", "date")
    search_fields = ("patient__email", "doctor__email", "notes")
    date_hierarchy = "date"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "exercise_type", "duration", "intensity", "calories_burned")
    list_filter = ("exercise_type", "date")
    search_fields = ("user__email", "notes")
    date_hierarchy = "date"


@admin.register(Sleep)
class SleepAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "sleep_time", "wake_time", "duration", "quality")
    list_filter = ("quality", "date")
    search_fields = ("user__email", "notes")
    date_hierarchy = "date"
