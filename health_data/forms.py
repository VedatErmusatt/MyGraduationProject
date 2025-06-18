from typing import Type

from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    Appointment,
    BloodTestResult,
    DailyActivity,
    Exercise,
    HealthTip,
    HospitalRecord,
    LabTestResult,
    Medication,
    Message,
    Sleep,
)


class MedicationForm(forms.ModelForm):
    reminder_times_str = forms.CharField(
        label="Hatırlatma Saatleri",
        help_text="Her bir saati HH:MM formatında girin. Birden fazla saat için virgül ile ayırın. (Örn: 08:00, 13:30, 19:51)",
        required=False,
    )

    class Meta:
        model = Medication
        fields = ["name", "dosage", "frequency", "start_date", "end_date", "notes", "is_active"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "data-date-format": "YYYY-MM-DD",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "data-date-format": "YYYY-MM-DD",
                }
            ),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "dosage": forms.TextInput(attrs={"class": "form-control"}),
            "frequency": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "İlaç Adı",
            "dosage": "Doz",
            "frequency": "Kullanım Sıklığı",
            "start_date": "Başlangıç Tarihi",
            "end_date": "Bitiş Tarihi",
            "notes": "Notlar",
            "is_active": "Aktif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mevcut saatleri string olarak göster
        if self.instance and self.instance.reminder_times:
            self.fields["reminder_times_str"].initial = ", ".join(self.instance.reminder_times)

        # Yeni kayıt için başlangıç tarihini bugün olarak ayarla
        if not self.instance.pk:
            self.initial["start_date"] = timezone.now().date()
        else:
            # Mevcut kayıt için tarihleri formatla
            if self.instance.start_date:
                self.initial["start_date"] = self.instance.start_date.strftime("%Y-%m-%d")
            if self.instance.end_date:
                self.initial["end_date"] = self.instance.end_date.strftime("%Y-%m-%d")

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("Bitiş tarihi başlangıç tarihinden önce olamaz.")

        return cleaned_data

    def clean_reminder_times_str(self):
        value = self.cleaned_data["reminder_times_str"]
        if not value:
            return []
        times = [t.strip() for t in value.split(",") if t.strip()]
        # Basit saat formatı kontrolü
        for t in times:
            try:
                hour, minute = map(int, t.split(":"))
                assert 0 <= hour < 24 and 0 <= minute < 60
            except Exception:
                raise forms.ValidationError("Saatler HH:MM formatında olmalı (örn: 19:51)")
        return times

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.reminder_times = self.cleaned_data["reminder_times_str"]
        if commit:
            instance.save()
        return instance


class ExerciseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format the date field value for HTML5 date input if instance exists
        if self.instance and self.instance.date:
            self.initial["date"] = self.instance.date.strftime("%Y-%m-%d")
        elif not self.instance.pk:  # If it's a new instance
            self.initial["date"] = timezone.now().strftime("%Y-%m-%d")

    class Meta:
        model = Exercise
        fields = ["exercise_type", "date", "duration", "intensity", "calories_burned", "notes"]
        widgets = {
            "exercise_type": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}),
            "intensity": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "10", "step": "1"}),
            "calories_burned": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "exercise_type": "Egzersiz Türü",
            "date": "Tarih",
            "duration": "Süre (dakika)",
            "intensity": "Yoğunluk (1-10)",
            "calories_burned": "Yakılan Kalori",
            "notes": "Notlar",
        }
        help_texts = {
            "duration": "Egzersiz süresini dakika cinsinden girin",
            "intensity": "Egzersiz yoğunluğunu 1 (çok hafif) ile 10 (çok yoğun) arasında belirtin",
            "calories_burned": "Yakılan kalori miktarını girin (isteğe bağlı)",
        }


class SleepForm(forms.ModelForm):
    class Meta:
        model = Sleep
        fields = ["date", "sleep_time", "wake_time", "quality", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sleep_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "wake_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "quality": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "date": "Tarih",
            "sleep_time": "Uyku Saati",
            "wake_time": "Uyanma Saati",
            "quality": "Uyku Kalitesi",
            "notes": "Notlar",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format the date field value for HTML5 date input if instance exists
        if self.instance and self.instance.date:
            self.initial["date"] = self.instance.date.strftime("%Y-%m-%d")
        elif not self.instance.pk:  # If it's a new instance
            self.initial["date"] = timezone.now().strftime("%Y-%m-%d")

    def clean(self):
        cleaned_data = super().clean()
        sleep_time = cleaned_data.get("sleep_time")
        wake_time = cleaned_data.get("wake_time")

        if sleep_time and wake_time:
            # Eğer uyanma saati uyku saatinden önceyse, ertesi güne geçmiş demektir
            if wake_time < sleep_time:
                # 24 saat ekleyerek süreyi hesapla
                duration = (wake_time.hour + 24 - sleep_time.hour) + (wake_time.minute - sleep_time.minute) / 60
            else:
                # Normal süre hesaplama
                duration = (wake_time.hour - sleep_time.hour) + (wake_time.minute - sleep_time.minute) / 60

            cleaned_data["duration"] = round(duration, 2)

        return cleaned_data


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["receiver", "subject", "content"]
        widgets = {
            "receiver": forms.Select(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
        labels = {
            "receiver": "Alıcı",
            "subject": "Konu",
            "content": "Mesaj",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.is_reply = kwargs.pop("is_reply", False)
        super().__init__(*args, **kwargs)
        User = get_user_model()

        if self.is_reply:
            # Yanıtlama durumunda alıcı alanını gizle
            del self.fields["receiver"]
        else:
            # Normal mesaj gönderme durumunda sadece doktorları listele
            self.fields["receiver"].queryset = User.objects.filter(groups__name="Doktorlar")
            if self.user:
                # Kendisini alıcı listesinden çıkar
                self.fields["receiver"].queryset = self.fields["receiver"].queryset.exclude(id=self.user.id)


class HospitalRecordForm(forms.ModelForm):
    class Meta:
        model = HospitalRecord
        fields = ["record_type", "date", "title", "description", "results", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "results": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


BloodTestResultFormSet: Type[forms.models.BaseInlineFormSet] = inlineformset_factory(
    HospitalRecord,
    BloodTestResult,
    fields=["parameter", "value", "unit", "reference_range", "is_abnormal"],
    extra=1,
    can_delete=True,
)

LabTestResultFormSet: Type[forms.models.BaseInlineFormSet] = inlineformset_factory(
    HospitalRecord, LabTestResult, fields=["test_name", "result", "interpretation"], extra=1, can_delete=True
)


class DailyActivityForm(forms.ModelForm):
    """Günlük aktivite formu"""

    class Meta:
        model = DailyActivity
        fields = ["steps", "water_intake", "notes"]
        widgets = {
            "steps": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "water_intake": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.1"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "steps": "Adım Sayısı",
            "water_intake": "Su Tüketimi (L)",
            "notes": "Notlar",
        }


class AppointmentForm(forms.ModelForm):
    """Randevu formu"""

    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time", "department", "notes"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "doctor": "Doktor",
            "date": "Tarih",
            "time": "Saat",
            "department": "Bölüm",
            "notes": "Notlar",
        }


class HealthTipForm(forms.ModelForm):
    """Sağlık ipucu formu"""

    class Meta:
        model = HealthTip
        fields = ["title", "content", "category", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title": "Başlık",
            "content": "İçerik",
            "category": "Kategori",
            "is_active": "Aktif",
        }
