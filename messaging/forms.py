from django import forms

from .models import Appointment, Message, Prescription


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["receiver", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            "patient",
            "diagnosis",
            "medications",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
