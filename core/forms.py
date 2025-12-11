from django import forms
from django.contrib.auth.models import User
from .models import Medicine, Reminder

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "dosage", "frequency", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full p-2 border rounded", "placeholder": "e.g., Paracetamol"}),
            "dosage": forms.TextInput(attrs={"class": "w-full p-2 border rounded", "placeholder": "e.g., 500 mg"}),
            "frequency": forms.TextInput(attrs={"class": "w-full p-2 border rounded", "placeholder": "e.g., Twice a day"}),
            "start_date": forms.DateInput(attrs={"class": "w-full p-2 border rounded", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "w-full p-2 border rounded", "type": "date"}),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["medicine", "reminder_time"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "w-full p-2 border rounded"}),
            "reminder_time": forms.DateTimeInput(attrs={"class": "w-full p-2 border rounded", "type": "datetime-local"}),
        }