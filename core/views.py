from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Medicine, Reminder
from .forms import SignupForm, MedicineForm, ReminderForm


def dashboard(request):
    medicines = Medicine.objects.all()
    reminders = Reminder.objects.filter(delivered=False)

    total_medicines = medicines.count()
    total_reminders = reminders.count()

    next_reminder = reminders.order_by('reminder_time').first()

    return render(request, "dashboard.html", {
        "total_medicines": total_medicines,
        "total_reminders": total_reminders,
        "next_dose_time": next_reminder.reminder_time if next_reminder else None,
        "next_dose_medicine": next_reminder.medicine.name if next_reminder else None,
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
    upcoming = Reminder.objects.filter(
        user=request.user,
        delivered=False
    ).order_by('reminder_time')

    past = Reminder.objects.filter(
        user=request.user,
        delivered=True
    ).order_by('-reminder_time')

    return render(request, "reminders.html", {
        "upcoming": upcoming,
        "past": past
    })


@login_required
def add_reminder(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.delivered = False

            # ✅ SAFE timezone handling
            if timezone.is_naive(reminder.reminder_time):
                reminder.reminder_time = timezone.make_aware(
                    reminder.reminder_time,
                    timezone.get_current_timezone()
                )

            reminder.save()
            messages.success(request, "Reminder added.")
            return redirect('reminders')
    else:
        form = ReminderForm()

    return render(request, "add_reminder.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        profile = request.user.userprofile
        profile.phone = request.POST.get("phone", "").strip()
        profile.save()
        return redirect('profile')
    return render(request, "profile.html")


@login_required
def profile_edit(request):
    profile = request.user.userprofile

    if request.method == "POST":
        profile.phone = request.POST.get("phone", "").strip()
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
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def medicines_list(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, "medicines_list.html", {"medicines": medicines})


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


@login_required
def delete_medicine(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        med.delete()
        messages.success(request, "Medicine deleted.")
        return redirect('medicines_list')
    return render(request, "confirm_delete.html", {"medicine": med})


@login_required
def edit_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk)

    if request.method == "POST":
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save(commit=False)

            if timezone.is_naive(reminder.reminder_time):
                reminder.reminder_time = timezone.make_aware(
                    reminder.reminder_time,
                    timezone.get_current_timezone()
                )

            reminder.save()
            messages.success(request, "Reminder updated.")
            return redirect('reminders')
    else:
        form = ReminderForm(instance=reminder)

    return render(request, "edit_reminder.html", {"form": form, "reminder": reminder})


@login_required
def delete_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk)
    if request.method == "POST":
        reminder.delete()
        messages.success(request, "Reminder deleted.")
        return redirect('reminders')
    return render(request, "confirm_delete_reminder.html", {"reminder": reminder})


@login_required
def api_get_reminders(request):
    reminders = Reminder.objects.filter(user=request.user, delivered=False)
    return JsonResponse([
        {
            "id": r.id,
            "medicine": r.medicine.name,
            "time": r.reminder_time.isoformat(),
            "delivered": r.delivered
        } for r in reminders
    ], safe=False)


@login_required
def api_mark_delivered(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    reminder.delivered = True
    reminder.save()
    return JsonResponse({"status": "ok"})
