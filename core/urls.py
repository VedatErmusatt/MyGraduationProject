from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/", views.notification_detail, name="notification_detail"),
    path(
        "notifications/mark-read/<int:pk>/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    path("health-tips/", views.health_tip_list, name="health_tip_list"),
    path("health-tips/<int:pk>/", views.health_tip_detail, name="health_tip_detail"),
    path(
        "emergency-contacts/",
        views.emergency_contact_list,
        name="emergency_contact_list",
    ),
    path(
        "emergency-contacts/add/",
        views.emergency_contact_add,
        name="emergency_contact_add",
    ),
    path(
        "emergency-contacts/<int:pk>/edit/",
        views.emergency_contact_edit,
        name="emergency_contact_edit",
    ),
    path(
        "emergency-contacts/<int:pk>/delete/",
        views.emergency_contact_delete,
        name="emergency_contact_delete",
    ),
]
