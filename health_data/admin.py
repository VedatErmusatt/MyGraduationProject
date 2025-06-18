# Register your models here.

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Appointment,
    DailyActivity,
    Exercise,
    HealthTip,
    Medication,
    Message,
    Sleep,
)


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
    list_display = ("patient", "doctor", "date", "time", "department", "is_active")
    list_filter = ("date", "is_active", "department")
    search_fields = (
        "patient__username",
        "patient__first_name",
        "patient__last_name",
        "doctor__username",
        "doctor__first_name",
        "doctor__last_name",
        "department",
        "notes",
    )
    date_hierarchy = "date"
    ordering = ("-date", "-time")


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


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "steps", "water_intake", "created_at")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__first_name", "user__last_name", "notes")
    date_hierarchy = "date"
    ordering = ("-date", "-created_at")


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
