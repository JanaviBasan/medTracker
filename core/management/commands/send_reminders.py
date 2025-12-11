# core/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from core.models import Reminder

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False


class Command(BaseCommand):
    help = "Send due reminders (email + optional SMS) and mark them delivered."

    def handle(self, *args, **options):
        now = timezone.now()
        due_qs = Reminder.objects.filter(delivered=False, reminder_time__lte=now)

        if not due_qs.exists():
            self.stdout.write("No due reminders.")
            return

        self.stdout.write(f"Found {due_qs.count()} due reminders. Sending...")

        twilio_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        twilio_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        twilio_from = getattr(settings, "TWILIO_FROM_NUMBER", None)

        if TWILIO_AVAILABLE and twilio_sid and twilio_token:
            twilio_client = TwilioClient(twilio_sid, twilio_token)
        else:
            twilio_client = None

        sent = 0
        with transaction.atomic():
            for r in due_qs.select_related("medicine", "user"):
                med_name = r.medicine.name
                time_str = r.reminder_time.strftime("%Y-%m-%d %H:%M")
                subject = f"MedCia reminder: {med_name}"
                body = f"Reminder for medicine: {med_name}\nTime: {time_str}\n\nThis is an automated reminder from MedCia."

                # Email
                to_email = None
                if getattr(r, "user", None) and r.user.email:
                    to_email = r.user.email

                if to_email:
                    try:
                        send_mail(
                            subject,
                            body,
                            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost"),
                            [to_email],
                            fail_silently=False,
                        )
                        self.stdout.write(f"Email sent to {to_email} for reminder {r.pk}")
                    except Exception as e:
                        self.stderr.write(f"Failed to send email for reminder {r.pk}: {e}")

                # SMS via Twilio (optional)
                phone = None
                if getattr(r, "user", None):
                    try:
                        phone = r.user.userprofile.phone
                    except Exception:
                        phone = None

                if phone and twilio_client and twilio_from:
                    try:
                        twilio_client.messages.create(
                            body=body,
                            from_=twilio_from,
                            to=phone
                        )
                        self.stdout.write(f"SMS sent to {phone} for reminder {r.pk}")
                    except Exception as e:
                        self.stderr.write(f"Failed to send SMS for reminder {r.pk}: {e}")

                # Mark delivered
                r.delivered = True
                r.save(update_fields=["delivered"])
                sent += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminders."))
