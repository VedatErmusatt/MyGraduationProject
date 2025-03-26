from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    # Appointment URLs
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/add/", views.appointment_add, name="appointment_add"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/edit/", views.appointment_edit, name="appointment_edit"),
    path(
        "appointments/<int:pk>/delete/",
        views.appointment_delete,
        name="appointment_delete",
    ),
    path(
        "appointments/<int:pk>/status/",
        views.appointment_status_change,
        name="appointment_status_change",
    ),
    # Message URLs
    path("messages/", views.message_list, name="message_list"),
    path("messages/send/", views.message_send, name="message_send"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/<int:pk>/delete/", views.message_delete, name="message_delete"),
    path(
        "messages/mark-read/<int:pk>/",
        views.message_mark_read,
        name="message_mark_read",
    ),
    # Prescription URLs
    path("prescriptions/", views.prescription_list, name="prescription_list"),
    path("prescriptions/add/", views.prescription_add, name="prescription_add"),
    path("prescriptions/<int:pk>/", views.prescription_detail, name="prescription_detail"),
    path(
        "prescriptions/<int:pk>/edit/",
        views.prescription_edit,
        name="prescription_edit",
    ),
    path(
        "prescriptions/<int:pk>/delete/",
        views.prescription_delete,
        name="prescription_delete",
    ),
]
