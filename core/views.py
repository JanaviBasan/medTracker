from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import make_aware

from .models import Medicine, Reminder
from .forms import SignupForm, MedicineForm, ReminderForm


def dashboard(request):
    medicines = Medicine.objects.all()
    reminders = Reminder.objects.all()

    # Count total medicines
    total_medicines = medicines.count()

    # Count total reminders
    total_reminders = reminders.count()

    # Calculate next upcoming reminder (next dose)
    next_reminder = reminders.order_by('reminder_time').first()

    if next_reminder:
        next_dose_time = next_reminder.reminder_time
        next_dose_medicine = next_reminder.medicine.name
    else:
        next_dose_time = None
        next_dose_medicine = None

    return render(request, "dashboard.html", {
        "total_medicines": total_medicines,
        "total_reminders": total_reminders,
        "next_dose_time": next_dose_time,
        "next_dose_medicine": next_dose_medicine,
    })


@login_required
def add_medicine(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine added.")
            return redirect('medicines_list')
    else:
        form = MedicineForm()
    return render(request, "add_medicine.html", {"form": form})


@login_required
def reminders(request):
    upcoming = Reminder.objects.filter(user=request.user, delivered=False).order_by('reminder_time')
    past = Reminder.objects.filter(user=request.user, delivered=True).order_by('-reminder_time')[:50]
    return render(request, "reminders.html", {"upcoming": upcoming, "past": past})

@login_required
def add_reminder(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user      # <-- assign logged-in user
            reminder.save()
            messages.success(request, "Reminder added.")
            return redirect('reminders')
    else:
        form = ReminderForm()
    return render(request, "add_reminder.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        profile = request.user.userprofile
        profile.phone = phone
        profile.save()
        return redirect('profile')
    return render(request, "profile.html")


@login_required
def profile_edit(request):
    profile = request.user.userprofile  # signal should have created this

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        profile.phone = phone
        profile.save()
        messages.success(request, "Profile updated.")
        return redirect('profile')

    return render(request, "profile_edit.html", {"profile": profile})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # auto-login
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


# --- Medicines list ---
@login_required
def medicines_list(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, "medicines_list.html", {"medicines": medicines})


# --- Edit medicine (GET shows form; POST saves) ---
@login_required
def edit_medicine(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated.")
            return redirect('medicines_list')
    else:
        form = MedicineForm(instance=med)
    return render(request, "edit_medicine.html", {"form": form, "medicine": med})


# --- Delete medicine (GET shows confirm; POST deletes) ---
@login_required
def delete_medicine(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        med.delete()
        messages.success(request, "Medicine deleted.")
        return redirect('medicines_list')
    return render(request, "confirm_delete.html", {"medicine": med})
