from django.urls import path

from . import views

app_name = "health_data"

urlpatterns = [
    # Hastane Kayıtları
    path("", views.HospitalRecordListView.as_view(), name="hospital_record_list"),
    path("create/", views.HospitalRecordCreateView.as_view(), name="hospital_record_create"),
    path("<int:pk>/", views.HospitalRecordDetailView.as_view(), name="hospital_record_detail"),
    path("<int:pk>/update/", views.HospitalRecordUpdateView.as_view(), name="hospital_record_update"),
    path("<int:pk>/delete/", views.HospitalRecordDeleteView.as_view(), name="hospital_record_delete"),
    # İlaçlar
    path("medications/", views.medication_list, name="medication_list"),
    path("medications/add/", views.medication_add, name="medication_add"),
    path("medications/<int:pk>/", views.medication_detail, name="medication_detail"),
    path("medications/<int:pk>/edit/", views.medication_edit, name="medication_edit"),
    path("medications/<int:pk>/delete/", views.medication_delete, name="medication_delete"),
    # Mesajlar
    path("messages/", views.message_list, name="message_list"),
    path("messages/send/", views.send_message, name="message_send"),
    path("messages/<int:message_id>/", views.message_detail, name="message_detail"),
    path("messages/<int:message_id>/delete/", views.message_delete, name="message_delete"),
    # Egzersizler
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/add/", views.exercise_add, name="exercise_add"),
    path("exercises/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("exercises/<int:pk>/edit/", views.exercise_edit, name="exercise_edit"),
    path("exercises/<int:pk>/delete/", views.exercise_delete, name="exercise_delete"),
    # Uyku
    path("sleep/", views.sleep_list, name="sleep_list"),
    path("sleep/add/", views.sleep_add, name="sleep_add"),
    path("sleep/<int:pk>/", views.sleep_detail, name="sleep_detail"),
    path("sleep/<int:pk>/edit/", views.sleep_edit, name="sleep_edit"),
    path("sleep/<int:pk>/delete/", views.sleep_delete, name="sleep_delete"),
]
