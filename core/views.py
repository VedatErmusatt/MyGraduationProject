# Create your views here.

import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from health_data.models import DailyActivity, Exercise, Medication, Sleep

from .forms import EmergencyContactForm
from .models import EmergencyContact, HealthTip, Notification


def home(request):
    """Ana sayfa görünümü"""
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    """Ana dashboard sayfası"""
    try:
        today = timezone.now().date()
        start_date = today - timedelta(days=7)

        # Aktif ilaçlar
        active_medications = Medication.objects.filter(
            user=request.user, is_active=True, start_date__lte=today, end_date__gte=today
        ).order_by("start_date")

        # Son 7 günün egzersizleri
        exercises = Exercise.objects.filter(user=request.user).order_by("-date")[:7]

        # Son 7 günün uyku kayıtları
        sleep_records = Sleep.objects.filter(user=request.user).order_by("-sleep_time")[:7]

        # Son 7 günlük uyku verileri
        sleep_data = Sleep.objects.filter(user=request.user, date__gte=start_date, date__lte=today).order_by("date")

        # Eksik günleri doldur
        all_dates = [(start_date + timedelta(days=x)) for x in range((today - start_date).days + 1)]
        sleep_dict = {sleep.date: float(sleep.duration) for sleep in sleep_data}
        sleep_labels = [date.strftime("%d.%m") for date in all_dates]
        sleep_durations = [sleep_dict.get(date, 0) for date in all_dates]

        # Egzersiz dağılımı
        exercise_data = (
            Exercise.objects.filter(user=request.user, date__gte=start_date, date__lte=today)
            .values("exercise_type")
            .annotate(count=Count("id"))
        )

        # Egzersiz türlerini Türkçe olarak al
        exercise_type_map = dict(Exercise.EXERCISE_TYPES)
        exercise_labels = [exercise_type_map.get(ex["exercise_type"], ex["exercise_type"]) for ex in exercise_data]
        exercise_counts = [ex["count"] for ex in exercise_data]

        # Günlük aktivite verileri
        daily_activity, created = DailyActivity.objects.get_or_create(
            user=request.user,
            defaults={
                "steps": 0,
                "water_intake": 0,
            },
        )

        # Günlük hedefler
        daily_goals = {
            "steps": 10000,
            "water": 2.5,  # Litre
            "sleep": 8,  # Saat
        }

        # Özet veriler
        summary_data = {
            "daily_steps": daily_activity.steps or 0,
            "daily_water": float(daily_activity.water_intake or 0),
            "calories_burned": Exercise.objects.filter(user=request.user, date=today).aggregate(
                total=Sum("calories_burned")
            )["total"]
            or 0,
            "avg_sleep": sleep_records.aggregate(avg=Avg("duration"))["avg"] or 0,
        }

        # Sağlık ipucu
        health_tip = HealthTip.objects.filter(is_active=True).order_by("?").first()

        context = {
            "active_medications": active_medications,
            "exercises": exercises,
            "sleep_records": sleep_records,
            "daily_goals": daily_goals,
            "summary_data": summary_data,
            "health_tip": health_tip,
            "daily_activity": daily_activity,
            "sleep_labels": json.dumps(sleep_labels),
            "sleep_durations": json.dumps(sleep_durations),
            "exercise_labels": json.dumps(exercise_labels),
            "exercise_counts": json.dumps(exercise_counts),
        }
        return render(request, "core/dashboard.html", context)
    except Exception as e:
        messages.error(request, f"Dashboard verileri yüklenirken bir hata oluştu: {str(e)}")
        return redirect("core:home")


@login_required
def notification_list(request):
    """Bildirim listesi görünümü"""
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "core/notification_list.html", {"notifications": notifications})


@login_required
def notification_detail(request, pk):
    """Bildirim detay görünümü"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, "core/notification_detail.html", {"notification": notification})


@login_required
def mark_notification_read(request, pk):
    """Bildirimi okundu olarak işaretle"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "success"})


def health_tip_list(request):
    """Sağlık ipuçları listesi görünümü"""
    tips = HealthTip.objects.filter(is_active=True)
    return render(request, "core/health_tip_list.html", {"tips": tips})


def health_tip_detail(request, pk):
    """Sağlık ipucu detay görünümü"""
    tip = get_object_or_404(HealthTip, pk=pk, is_active=True)
    return render(request, "core/health_tip_detail.html", {"tip": tip})


@login_required
def emergency_contact_list(request):
    """Acil durum kontakları listesi görünümü"""
    contacts = EmergencyContact.objects.filter(user=request.user)
    return render(request, "core/emergency_contact_list.html", {"contacts": contacts})


@login_required
def emergency_contact_add(request):
    """Acil durum kontağı ekleme görünümü"""
    if request.method == "POST":
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, "Acil durum kontağı başarıyla eklendi.")
            return redirect("core:emergency_contact_list")
    else:
        form = EmergencyContactForm()
    return render(
        request,
        "core/emergency_contact_form.html",
        {"form": form, "title": "Yeni Acil Durum Kontağı"},
    )


@login_required
def emergency_contact_edit(request, pk):
    """Acil durum kontağı düzenleme görünümü"""
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == "POST":
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Acil durum kontağı başarıyla güncellendi.")
            return redirect("core:emergency_contact_list")
    else:
        form = EmergencyContactForm(instance=contact)
    return render(
        request,
        "core/emergency_contact_form.html",
        {"form": form, "title": "Acil Durum Kontağını Düzenle"},
    )


@login_required
def emergency_contact_delete(request, pk):
    """Acil durum kontağı silme görünümü"""
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Acil durum kontağı başarıyla silindi.")
        return redirect("core:emergency_contact_list")
    return render(request, "core/emergency_contact_confirm_delete.html", {"contact": contact})
