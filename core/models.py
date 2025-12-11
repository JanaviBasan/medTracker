from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)  # e.g., "500 mg"
    frequency = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
class Reminder(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicine.name} at {self.reminder_time}"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
