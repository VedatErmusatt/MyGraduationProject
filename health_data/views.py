# Create your views here.

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    AppointmentForm,
    DailyActivityForm,
    ExerciseForm,
    HospitalRecordForm,
    MedicationForm,
    MessageForm,
    SleepForm,
)
from .models import (
    Appointment,
    DailyActivity,
    Exercise,
    HealthTip,
    HospitalRecord,
    Medication,
    Message,
    MotivationVideo,
    Sleep,
)
from .utils import send_message_notification_email


def is_doctor(user):
    return user.is_authenticated and user.is_doctor


# Medication Views
@login_required
def medication_list(request):
    """İlaç listesi görünümü"""
    medications = Medication.objects.filter(user=request.user).order_by("-start_date")
    return render(request, "health_data/medication_list.html", {"medications": medications})


@login_required
def medication_add(request):
    """İlaç ekleme görünümü"""
    if request.method == "POST":
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user
            medication.save()
            messages.success(request, "İlaç başarıyla kaydedildi.")
            return redirect("health_data:medication_list")
    else:
        form = MedicationForm()
    return render(request, "health_data/medication_form.html", {"form": form})


@login_required
def medication_detail(request, pk):
    """İlaç detay görünümü"""
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    return render(request, "health_data/medication_detail.html", {"medication": medication})


@login_required
def medication_edit(request, pk):
    """İlaç düzenleme görünümü"""
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == "POST":
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            messages.success(request, "İlaç başarıyla güncellendi.")
            return redirect("health_data:medication_list")
    else:
        form = MedicationForm(instance=medication)
    return render(request, "health_data/medication_form.html", {"form": form})


@login_required
def medication_delete(request, pk):
    """İlaç silme görünümü"""
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == "POST":
        medication.delete()
        messages.success(request, "İlaç başarıyla silindi.")
        return redirect("health_data:medication_list")
    return render(request, "health_data/medication_delete.html", {"medication": medication})


# Exercise Views
@login_required
def exercise_list(request):
    """Egzersiz listesi görünümü"""
    exercises = Exercise.objects.filter(user=request.user).order_by("-date")
    return render(request, "health_data/exercise_list.html", {"exercises": exercises})


@login_required
def exercise_add(request):
    """Egzersiz ekleme görünümü"""
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.save()
            messages.success(request, "Egzersiz başarıyla kaydedildi.")
            return redirect("health_data:exercise_list")
    else:
        form = ExerciseForm()
    return render(request, "health_data/exercise_form.html", {"form": form})


@login_required
def exercise_detail(request, pk):
    """Egzersiz detay görünümü"""
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    return render(request, "health_data/exercise_detail.html", {"exercise": exercise})


@login_required
def exercise_edit(request, pk):
    """Egzersiz düzenleme görünümü"""
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, "Egzersiz başarıyla güncellendi.")
            return redirect("health_data:exercise_list")
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, "health_data/exercise_form.html", {"form": form})


@login_required
def exercise_delete(request, pk):
    """Egzersiz silme görünümü"""
    exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
    if request.method == "POST":
        exercise.delete()
        messages.success(request, "Egzersiz başarıyla silindi.")
        return redirect("health_data:exercise_list")
    return render(request, "health_data/exercise_delete.html", {"exercise": exercise})


# Sleep Views
@login_required
def sleep_list(request):
    """Uyku kayıtları listesi"""
    sleeps = Sleep.objects.filter(user=request.user).order_by("-sleep_time")
    return render(request, "health_data/sleep_list.html", {"sleeps": sleeps})


@login_required
def sleep_add(request):
    """Yeni uyku kaydı ekleme"""
    if request.method == "POST":
        form = SleepForm(request.POST)
        if form.is_valid():
            sleep = form.save(commit=False)
            sleep.user = request.user
            sleep.duration = form.cleaned_data["duration"]  # Hesaplanan süreyi kaydet
            sleep.save()
            messages.success(request, "Uyku kaydı başarıyla eklendi.")
            return redirect("health_data:sleep_list")
    else:
        form = SleepForm()
    return render(request, "health_data/sleep_form.html", {"form": form, "sleep": None})


@login_required
def sleep_detail(request, pk):
    """Uyku kaydı detayı"""
    sleep = get_object_or_404(Sleep, pk=pk, user=request.user)
    return render(request, "health_data/sleep_detail.html", {"sleep": sleep})


@login_required
def sleep_edit(request, pk):
    """Uyku kaydı düzenleme"""
    sleep = get_object_or_404(Sleep, pk=pk, user=request.user)
    if request.method == "POST":
        form = SleepForm(request.POST, instance=sleep)
        if form.is_valid():
            form.save()
            messages.success(request, "Uyku kaydı başarıyla güncellendi.")
            return redirect("health_data:sleep_list")
    else:
        form = SleepForm(instance=sleep)
    return render(request, "health_data/sleep_form.html", {"form": form, "sleep": sleep})


@login_required
def sleep_delete(request, pk):
    """Uyku kaydı silme"""
    sleep = get_object_or_404(Sleep, pk=pk, user=request.user)
    if request.method == "POST":
        sleep.delete()
        messages.success(request, "Uyku kaydı başarıyla silindi.")
        return redirect("health_data:sleep_list")
    return render(request, "health_data/sleep_delete.html", {"sleep": sleep})


@login_required
def update_daily_activity(request):
    """Günlük aktivite güncelleme"""

    if request.method == "POST":
        form = DailyActivityForm(request.POST)
        if form.is_valid():
            # Use update_or_create to handle the unique constraint
            daily_activity, created = DailyActivity.objects.update_or_create(
                user=request.user,
                defaults={
                    "steps": form.cleaned_data["steps"],
                    "water_intake": form.cleaned_data["water_intake"],
                    "notes": form.cleaned_data["notes"],
                },
            )
            messages.success(request, "Günlük aktivite başarıyla güncellendi.")
            return redirect("core:dashboard")
    else:
        # Get existing record or initialize empty form
        daily_activity = DailyActivity.objects.filter(user=request.user).first()
        form = DailyActivityForm(instance=daily_activity if daily_activity else None)

    return render(request, "health_data/daily_activity_form.html", {"form": form})


@login_required
def appointment_list(request):
    """Randevu listesi"""
    appointments = Appointment.objects.filter(patient=request.user).order_by("-date", "-time")

    return render(request, "health_data/appointment_list.html", {"appointments": appointments})


@login_required
def appointment_create(request):
    """Yeni randevu oluşturma"""
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            messages.success(request, "Randevu başarıyla oluşturuldu.")
            return redirect("health_data:appointment_list")
    else:
        form = AppointmentForm()

    return render(request, "health_data/appointment_form.html", {"form": form})


@login_required
def appointment_detail(request, pk):
    """Randevu detayı"""
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    return render(request, "health_data/appointment_detail.html", {"appointment": appointment})


@login_required
def appointment_update(request, pk):
    """Randevu güncelleme"""
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Randevu başarıyla güncellendi.")
            return redirect("health_data:appointment_detail", pk=pk)
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "health_data/appointment_form.html", {"form": form})


@login_required
def appointment_delete(request, pk):
    """Randevu silme"""
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Randevu başarıyla silindi.")
        return redirect("health_data:appointment_list")

    return render(request, "health_data/appointment_confirm_delete.html", {"appointment": appointment})


@login_required
def health_tips(request):
    """Sağlık ipuçları listesi"""
    tips = HealthTip.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "health_data/health_tips.html", {"tips": tips})


@login_required
def health_tip_detail(request, pk):
    """Sağlık ipucu detayı"""
    tip = get_object_or_404(HealthTip, pk=pk, is_active=True)
    return render(request, "health_data/health_tip_detail.html", {"tip": tip})


@login_required
def health_reports(request):
    """Sağlık raporları görünümü"""
    # Son 30 günlük veriler
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Egzersiz istatistikleri
    exercise_stats = Exercise.objects.filter(user=request.user, date__range=[start_date, end_date]).aggregate(
        total_duration=Sum("duration"),
        avg_intensity=Avg("intensity"),
        total_calories=Sum("calories_burned"),
    )

    # Uyku istatistikleri
    sleep_stats = Sleep.objects.filter(user=request.user, start_time__range=[start_date, end_date]).aggregate(
        avg_quality=Avg("quality"), total_duration=Sum("duration")
    )

    context = {
        "exercise_stats": exercise_stats,
        "sleep_stats": sleep_stats,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "health_data/health_reports.html", context)


@login_required
def message_list(request):
    """Mesaj listesi görünümü"""
    received_messages = Message.objects.filter(receiver=request.user).order_by("-created_at")
    sent_messages = Message.objects.filter(sender=request.user).order_by("-created_at")

    # Okunmamış mesaj sayısı
    unread_count = received_messages.filter(is_read=False).count()

    context = {
        "received_messages": received_messages,
        "sent_messages": sent_messages,
        "unread_count": unread_count,
    }
    return render(request, "health_data/message_list.html", context)


@login_required
def message_detail(request, message_id):
    """Mesaj detay görünümü"""
    message = get_object_or_404(Message, id=message_id)

    # Mesajı okundu olarak işaretle
    if message.receiver == request.user and not message.is_read:
        message.mark_as_read()

    # Yanıtları getir
    replies = Message.objects.filter(parent_message=message).order_by("created_at")

    context = {
        "message": message,
        "replies": replies,
    }
    return render(request, "health_data/message_detail.html", context)


@login_required
def send_message(request, reply_to=None):
    """Yeni mesaj gönderme veya yanıtlama görünümü"""
    if reply_to:
        parent_message = get_object_or_404(Message, id=reply_to)
        # Yanıtlanan mesajın alıcısı veya göndereni olmalıyız
        if request.user not in [parent_message.sender, parent_message.receiver]:
            raise PermissionDenied
        initial = {
            "receiver": parent_message.sender if request.user == parent_message.receiver else parent_message.receiver,
            "subject": f"Re: {parent_message.subject}",
        }
        is_reply = True
    else:
        parent_message = None
        initial = {}
        is_reply = False

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if parent_message:
                message.parent_message = parent_message
            message.save()

            # Email bildirimi gönder
            try:
                send_message_notification_email(message)
            except Exception:
                # Email gönderimi başarısız olsa bile mesaj kaydedildi
                messages.warning(request, "Mesaj gönderildi fakat email bildirimi gönderilemedi.")

            messages.success(request, "Mesajınız başarıyla gönderildi.")
            return redirect("health_data:message_list")
    else:
        form = MessageForm(initial=initial)

    context = {
        "form": form,
        "parent_message": parent_message,
        "is_reply": is_reply,
    }
    return render(request, "health_data/message_form.html", context)


@login_required
def message_delete(request, message_id):
    """Mesaj silme görünümü"""
    message = get_object_or_404(Message, id=message_id)

    # Sadece mesajın göndereni veya alıcısı silebilir
    if message.sender != request.user and message.receiver != request.user:
        raise PermissionDenied

    if request.method == "POST":
        message.delete()
        messages.success(request, "Mesaj başarıyla silindi.")
        return redirect("health_data:message_list")

    return render(request, "health_data/message_confirm_delete.html", {"message": message})


class HospitalRecordListView(LoginRequiredMixin, ListView):
    model = HospitalRecord
    template_name = "health_data/hospital_record_list.html"
    context_object_name = "records"

    def get_queryset(self):
        if self.request.user.is_doctor:
            # Doktorlar tüm kayıtları görebilir
            return HospitalRecord.objects.all()
        else:
            # Normal kullanıcılar sadece kendi kayıtlarını görebilir
            return HospitalRecord.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = context["records"]

        # Kayıtları türlerine göre grupla
        context["interventions"] = records.filter(record_type="intervention")
        context["xrays"] = records.filter(record_type="xray")
        context["blood_tests"] = records.filter(record_type="blood_test")
        context["lab_tests"] = records.filter(record_type="lab_test")
        context["imaging"] = records.filter(record_type="imaging")
        context["treatments"] = records.filter(record_type="treatment")

        return context


class HospitalRecordDetailView(LoginRequiredMixin, DetailView):
    model = HospitalRecord
    template_name = "health_data/hospital_record_detail.html"
    context_object_name = "record"

    def get_queryset(self):
        if self.request.user.is_doctor:
            return HospitalRecord.objects.all()
        return HospitalRecord.objects.filter(user=self.request.user)


class HospitalRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = HospitalRecord
    form_class = HospitalRecordForm
    template_name = "health_data/hospital_record_form.html"
    success_url = reverse_lazy("health_data:hospital_record_list")

    def test_func(self):
        return is_doctor(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Sadece doktorlar hastane kaydı ekleyebilir.")
        return HttpResponseForbidden()

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        messages.success(self.request, "Hastane kaydı başarıyla oluşturuldu.")
        return super().form_valid(form)


class HospitalRecordUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HospitalRecord
    form_class = HospitalRecordForm
    template_name = "health_data/hospital_record_form.html"
    success_url = reverse_lazy("health_data:hospital_record_list")

    def test_func(self):
        return is_doctor(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Sadece doktorlar hastane kaydı düzenleyebilir.")
        return HttpResponseForbidden()

    def form_valid(self, form):
        messages.success(self.request, "Hastane kaydı başarıyla güncellendi.")
        return super().form_valid(form)


class HospitalRecordDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HospitalRecord
    template_name = "health_data/hospital_record_confirm_delete.html"
    success_url = reverse_lazy("health_data:hospital_record_list")

    def test_func(self):
        return is_doctor(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Sadece doktorlar hastane kaydı silebilir.")
        return HttpResponseForbidden()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Hastane kaydı başarıyla silindi.")
        return super().delete(request, *args, **kwargs)


@login_required
def motivation_videos(request):
    """Motivasyon videoları listesi"""
    category = request.GET.get("category", "")
    videos = MotivationVideo.objects.filter(is_active=True)

    if category:
        videos = videos.filter(category=category)

    categories = dict(MotivationVideo.CATEGORY_CHOICES)

    context = {
        "videos": videos,
        "categories": categories,
        "selected_category": category,
    }
    return render(request, "health_data/motivation_videos.html", context)
