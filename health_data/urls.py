from django.urls import path

from . import views

app_name = "health_data"

urlpatterns = [
    # Reports
    path("reports/", views.health_reports, name="health_reports"),
    # Vital Signs URLs
    path("vitals/", views.vital_signs_list, name="vital_signs_list"),
    path("vitals/add/", views.vital_signs_add, name="vital_signs_add"),
    path("vitals/<int:pk>/", views.vital_signs_detail, name="vital_signs_detail"),
    path("vitals/<int:pk>/edit/", views.vital_signs_edit, name="vital_signs_edit"),
    path("vitals/<int:pk>/delete/", views.vital_signs_delete, name="vital_signs_delete"),
    # Medication URLs
    path("medications/", views.medication_list, name="medication_list"),
    path("medications/add/", views.medication_add, name="medication_add"),
    path("medications/<int:pk>/", views.medication_detail, name="medication_detail"),
    path("medications/<int:pk>/edit/", views.medication_edit, name="medication_edit"),
    path("medications/<int:pk>/delete/", views.medication_delete, name="medication_delete"),
    # Exercise URLs
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/add/", views.exercise_add, name="exercise_add"),
    path("exercises/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("exercises/<int:pk>/edit/", views.exercise_edit, name="exercise_edit"),
    path("exercises/<int:pk>/delete/", views.exercise_delete, name="exercise_delete"),
    # Sleep URLs
    path("sleep/", views.sleep_list, name="sleep_list"),
    path("sleep/add/", views.sleep_add, name="sleep_add"),
    path("sleep/<int:pk>/", views.sleep_detail, name="sleep_detail"),
    path("sleep/<int:pk>/edit/", views.sleep_edit, name="sleep_edit"),
    path("sleep/<int:pk>/delete/", views.sleep_delete, name="sleep_delete"),
    # Messages
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:message_id>/", views.message_detail, name="message_detail"),
    path("messages/send/", views.send_message, name="message_send"),
    path("messages/send/<int:reply_to>/", views.send_message, name="message_reply"),
    path("messages/<int:message_id>/delete/", views.message_delete, name="message_delete"),
    # Dashboard and Reports
    path("dashboard/", views.health_dashboard, name="health_dashboard"),
]
