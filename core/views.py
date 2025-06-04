# Create your views here.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from health_data.models import Exercise, Medication, Sleep

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
    # Aktif ilaçlar
    medications = Medication.objects.filter(user=request.user, is_active=True)
    print(f"Aktif ilaç sayısı: {medications.count()}")

    # Son 7 günün egzersizleri
    exercises = Exercise.objects.filter(user=request.user).order_by("-date")[:7]
    print(f"Egzersiz sayısı: {exercises.count()}")

    # Son 7 günün uyku kayıtları
    sleep_records = Sleep.objects.filter(user=request.user).order_by("-sleep_time")[:7]
    print(f"Uyku kaydı sayısı: {sleep_records.count()}")

    context = {
        "medications": medications,
        "exercises": exercises,
        "sleep_records": sleep_records,
    }
    return render(request, "users/dashboard.html", context)


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
