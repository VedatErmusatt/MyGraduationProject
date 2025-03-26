# Create your views here.

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExerciseForm, MedicationForm, SleepForm, VitalSignsForm
from .models import Exercise, Medication, Sleep, VitalSigns


# Vital Signs Views
@login_required
def vital_signs_list(request):
    """Vital bulgular listesi görünümü"""
    vitals = VitalSigns.objects.filter(user=request.user).order_by("-date")
    return render(request, "health_data/vital_signs_list.html", {"vitals": vitals})


@login_required
def vital_signs_add(request):
    """Vital bulgu ekleme görünümü"""
    if request.method == "POST":
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vital = form.save(commit=False)
            vital.user = request.user
            vital.save()
            messages.success(request, "Vital bulgular başarıyla kaydedildi.")
            return redirect("health_data:vital_signs_list")
    else:
        form = VitalSignsForm()
    return render(request, "health_data/vital_signs_form.html", {"form": form})


@login_required
def vital_signs_detail(request, pk):
    """Vital bulgu detay görünümü"""
    vital = get_object_or_404(VitalSigns, pk=pk, user=request.user)
    return render(request, "health_data/vital_signs_detail.html", {"vital": vital})


@login_required
def vital_signs_edit(request, pk):
    """Vital bulgu düzenleme görünümü"""
    vital = get_object_or_404(VitalSigns, pk=pk, user=request.user)
    if request.method == "POST":
        form = VitalSignsForm(request.POST, instance=vital)
        if form.is_valid():
            form.save()
            messages.success(request, "Vital bulgular başarıyla güncellendi.")
            return redirect("health_data:vital_signs_list")
    else:
        form = VitalSignsForm(instance=vital)
    return render(request, "health_data/vital_signs_form.html", {"form": form})


@login_required
def vital_signs_delete(request, pk):
    """Vital bulgu silme görünümü"""
    vital = get_object_or_404(VitalSigns, pk=pk, user=request.user)
    if request.method == "POST":
        vital.delete()
        messages.success(request, "Vital bulgular başarıyla silindi.")
        return redirect("health_data:vital_signs_list")
    return render(request, "health_data/vital_signs_delete.html", {"vital": vital})


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


# Dashboard and Reports
@login_required
def health_dashboard(request):
    """Kullanıcının sağlık verilerinin özet görünümü"""
    print(f"Giriş yapmış kullanıcı: {request.user.email}")  # Debug için

    # Son 7 günlük vital bulgular
    vitals = VitalSigns.objects.filter(user=request.user).order_by("-date")[:7]
    print(f"Vital bulgular sayısı: {vitals.count()}")  # Debug için

    # Aktif ilaçlar
    medications = Medication.objects.filter(user=request.user, is_active=True)
    print(f"Aktif ilaç sayısı: {medications.count()}")  # Debug için

    # Son 7 günlük egzersizler
    exercises = Exercise.objects.filter(user=request.user).order_by("-date")[:7]
    print(f"Egzersiz sayısı: {exercises.count()}")  # Debug için

    # Son 7 günlük uyku kayıtları
    sleeps = Sleep.objects.filter(user=request.user).order_by("-date")[:7]
    print(f"Uyku kaydı sayısı: {sleeps.count()}")  # Debug için

    context = {
        "vitals": vitals,
        "medications": medications,
        "exercises": exercises,
        "sleeps": sleeps,
    }
    return render(request, "health_data/health_dashboard.html", context)


@login_required
def health_reports(request):
    """Sağlık raporları görünümü"""
    # Son 30 günlük veriler
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Vital bulgular trendi
    vital_trends = VitalSigns.objects.filter(user=request.user, date__range=[start_date, end_date]).order_by("date")

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
        "vital_trends": vital_trends,
        "exercise_stats": exercise_stats,
        "sleep_stats": sleep_stats,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "health_data/health_reports.html", context)
