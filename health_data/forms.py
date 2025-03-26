from django import forms
from django.utils import timezone

from .models import Exercise, Medication, Sleep, VitalSigns


class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "heart_rate",
            "temperature",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ["name", "dosage", "frequency", "start_date", "end_date", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["date", "duration", "intensity", "calories_burned", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}),
            "intensity": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "10", "step": "1"}),
            "calories_burned": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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
        if not self.instance.pk:  # Yeni kayıt oluşturuluyorsa
            self.initial["date"] = timezone.now().date()

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
