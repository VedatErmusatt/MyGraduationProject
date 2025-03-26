# Register your models here.

from django.contrib import admin

from .models import Appointment, Message, Prescription


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "time", "status")
    list_filter = ("status", "date", "doctor", "patient")
    search_fields = ("patient__username", "doctor__username", "notes")
    date_hierarchy = "date"
    ordering = ("-date", "-time")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "content", "is_read", "created_at")
    list_filter = ("is_read", "created_at", "sender", "receiver")
    search_fields = ("sender__username", "receiver__username", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "date", "is_active")
    list_filter = ("is_active", "date", "doctor", "patient")
    search_fields = (
        "doctor__username",
        "patient__username",
        "diagnosis",
        "medications",
    )
    date_hierarchy = "date"
    ordering = ("-date",)
