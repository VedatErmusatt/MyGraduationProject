# Register your models here.

from django.contrib import admin

from .models import Exercise, Medication, Sleep, VitalSigns


@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "blood_pressure_systolic",
        "blood_pressure_diastolic",
        "heart_rate",
        "temperature",
        "blood_sugar",
    )
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__email", "notes")
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "dosage",
        "frequency",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("is_active", "start_date", "end_date", "user")
    search_fields = ("name", "user__username", "user__email", "notes")
    date_hierarchy = "start_date"
    ordering = ("-start_date",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "exercise_type",
        "duration",
        "intensity",
        "calories_burned",
    )
    list_filter = ("exercise_type", "date", "user")
    search_fields = ("user__username", "user__email", "notes")
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(Sleep)
class SleepAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "sleep_time", "wake_time", "quality", "duration")
    list_filter = ("quality", "date", "user")
    search_fields = ("user__username", "user__email", "notes")
    date_hierarchy = "date"
    ordering = ("-date",)
