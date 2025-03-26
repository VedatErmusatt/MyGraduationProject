# Create your views here.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AppointmentForm, MessageForm, PrescriptionForm
from .models import Appointment, Message, Prescription


# Appointment Views
@login_required
def appointment_list(request):
    """Randevu listesi görünümü"""
    if request.user.is_doctor:
        appointments = Appointment.objects.filter(doctor=request.user).order_by("-date", "-time")
    else:
        appointments = Appointment.objects.filter(patient=request.user).order_by("-date", "-time")
    return render(request, "messaging/appointment_list.html", {"appointments": appointments})


@login_required
def appointment_add(request):
    """Randevu ekleme görünümü"""
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if request.user.is_doctor:
                appointment.doctor = request.user
            else:
                appointment.patient = request.user
            appointment.save()
            messages.success(request, "Randevu başarıyla oluşturuldu.")
            return redirect("messaging:appointment_list")
    else:
        form = AppointmentForm()
    return render(
        request,
        "messaging/appointment_form.html",
        {"form": form, "title": "Yeni Randevu"},
    )


@login_required
def appointment_detail(request, pk):
    """Randevu detay görünümü"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if not (request.user == appointment.doctor or request.user == appointment.patient):
        messages.error(request, "Bu randevuya erişim yetkiniz yok.")
        return redirect("messaging:appointment_list")
    return render(request, "messaging/appointment_detail.html", {"appointment": appointment})


@login_required
def appointment_edit(request, pk):
    """Randevu düzenleme görünümü"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if not (request.user == appointment.doctor or request.user == appointment.patient):
        messages.error(request, "Bu randevuyu düzenleme yetkiniz yok.")
        return redirect("messaging:appointment_list")
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Randevu başarıyla güncellendi.")
            return redirect("messaging:appointment_list")
    else:
        form = AppointmentForm(instance=appointment)
    return render(
        request,
        "messaging/appointment_form.html",
        {"form": form, "title": "Randevuyu Düzenle"},
    )


@login_required
def appointment_delete(request, pk):
    """Randevu silme görünümü"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if not (request.user == appointment.doctor or request.user == appointment.patient):
        messages.error(request, "Bu randevuyu silme yetkiniz yok.")
        return redirect("messaging:appointment_list")
    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Randevu başarıyla silindi.")
        return redirect("messaging:appointment_list")
    return render(
        request,
        "messaging/appointment_confirm_delete.html",
        {"appointment": appointment},
    )


@login_required
def appointment_status_change(request, pk):
    """Randevu durumu değiştirme görünümü"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user != appointment.doctor:
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect("messaging:appointment_list")
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, "Randevu durumu güncellendi.")
    return redirect("messaging:appointment_detail", pk=pk)


# Message Views
@login_required
def message_list(request):
    """Mesaj listesi görünümü"""
    messages_list = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by("-created_at")
    return render(request, "messaging/message_list.html", {"messages": messages_list})


@login_required
def message_send(request):
    """Mesaj gönderme görünümü"""
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Mesaj başarıyla gönderildi.")
            return redirect("messaging:message_list")
    else:
        form = MessageForm()
    return render(request, "messaging/message_form.html", {"form": form, "title": "Yeni Mesaj"})


@login_required
def message_detail(request, pk):
    """Mesaj detay görünümü"""
    message = get_object_or_404(Message, pk=pk)
    if not (request.user == message.sender or request.user == message.receiver):
        messages.error(request, "Bu mesaja erişim yetkiniz yok.")
        return redirect("messaging:message_list")
    if request.user == message.receiver and not message.is_read:
        message.is_read = True
        message.save()
    return render(request, "messaging/message_detail.html", {"message": message})


@login_required
def message_delete(request, pk):
    """Mesaj silme görünümü"""
    message = get_object_or_404(Message, pk=pk)
    if request.user != message.sender:
        messages.error(request, "Bu mesajı silme yetkiniz yok.")
        return redirect("messaging:message_list")
    if request.method == "POST":
        message.delete()
        messages.success(request, "Mesaj başarıyla silindi.")
        return redirect("messaging:message_list")
    return render(request, "messaging/message_confirm_delete.html", {"message": message})


@login_required
def message_mark_read(request, pk):
    """Mesajı okundu olarak işaretle"""
    message = get_object_or_404(Message, pk=pk, receiver=request.user)
    message.is_read = True
    message.save()
    return JsonResponse({"status": "success"})


# Prescription Views
@login_required
def prescription_list(request):
    """Reçete listesi görünümü"""
    if request.user.is_doctor:
        prescriptions = Prescription.objects.filter(doctor=request.user).order_by("-date")
    else:
        prescriptions = Prescription.objects.filter(patient=request.user).order_by("-date")
    return render(request, "messaging/prescription_list.html", {"prescriptions": prescriptions})


@login_required
def prescription_add(request):
    """Reçete ekleme görünümü"""
    if not request.user.is_doctor:
        messages.error(request, "Bu işlem için doktor yetkisi gereklidir.")
        return redirect("messaging:prescription_list")
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user
            prescription.save()
            messages.success(request, "Reçete başarıyla oluşturuldu.")
            return redirect("messaging:prescription_list")
    else:
        form = PrescriptionForm()
    return render(
        request,
        "messaging/prescription_form.html",
        {"form": form, "title": "Yeni Reçete"},
    )


@login_required
def prescription_detail(request, pk):
    """Reçete detay görünümü"""
    prescription = get_object_or_404(Prescription, pk=pk)
    if not (request.user == prescription.doctor or request.user == prescription.patient):
        messages.error(request, "Bu reçeteye erişim yetkiniz yok.")
        return redirect("messaging:prescription_list")
    return render(request, "messaging/prescription_detail.html", {"prescription": prescription})


@login_required
def prescription_edit(request, pk):
    """Reçete düzenleme görünümü"""
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.user != prescription.doctor:
        messages.error(request, "Bu reçeteyi düzenleme yetkiniz yok.")
        return redirect("messaging:prescription_list")
    if request.method == "POST":
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            messages.success(request, "Reçete başarıyla güncellendi.")
            return redirect("messaging:prescription_list")
    else:
        form = PrescriptionForm(instance=prescription)
    return render(
        request,
        "messaging/prescription_form.html",
        {"form": form, "title": "Reçeteyi Düzenle"},
    )


@login_required
def prescription_delete(request, pk):
    """Reçete silme görünümü"""
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.user != prescription.doctor:
        messages.error(request, "Bu reçeteyi silme yetkiniz yok.")
        return redirect("messaging:prescription_list")
    if request.method == "POST":
        prescription.delete()
        messages.success(request, "Reçete başarıyla silindi.")
        return redirect("messaging:prescription_list")
    return render(
        request,
        "messaging/prescription_confirm_delete.html",
        {"prescription": prescription},
    )
