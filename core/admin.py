# Register your models here.

from django.contrib import admin

from .models import EmergencyContact, HealthTip, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at", "user")
    search_fields = ("user__username", "title", "message")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at", "is_active")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "relationship", "phone_number")
    list_filter = ("relationship", "user")
    search_fields = ("user__username", "name", "phone_number", "email")
    ordering = ("user", "name")
