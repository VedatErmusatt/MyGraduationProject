from django import forms

from .models import EmergencyContact


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ["name", "relationship", "phone_number", "email", "address", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
