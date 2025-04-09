from django.db import models
from accounts.models import User


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments')
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counselor_appointments', 
                                limit_choices_to={'user_type': 'counselor'})
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField(help_text="Brief description of the reason for appointment")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment with {self.counselor.username} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"


class AppointmentReminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    sent_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=(('email', 'Email'), ('sms', 'SMS')))
    
    def __str__(self):
        return f"Reminder for appointment #{self.appointment.id} sent via {self.method}"


class TimeSlot(models.Model):
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots', 
                                limit_choices_to={'user_type': 'counselor'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    # Add a reference to the appointment if booked
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='time_slot')
    
    def __str__(self):
        return f"{self.counselor.username}: {self.date} {self.start_time}-{self.end_time}"
    
    class Meta:
        unique_together = ['counselor', 'date', 'start_time']
        ordering = ['date', 'start_time']
        
    @property
    def formatted_time(self):
        """Return a formatted string of the time slot"""
        start = self.start_time.strftime('%I:%M %p')
        end = self.end_time.strftime('%I:%M %p')
        return f"{start} - {end}"
    
    @property
    def is_past(self):
        """Check if this time slot is in the past"""
        from django.utils import timezone
        import datetime
        
        today = timezone.now().date()
        now = timezone.now().time()
        
        if self.date < today:
            return True
        elif self.date == today and self.end_time < now:
            return True
        return False