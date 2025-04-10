from django import forms
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model
from accounts.models import User
from .models import Appointment, TimeSlot 


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Optional: Describe the reason for your appointment'}),
        }


class TimeSlotForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select a date for the time slot"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Start time (e.g., 09:00)"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="End time (e.g., 10:00)"
    )
    
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time']
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time and date:
            # Check that end time is after start time
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time.')
            
            # Check that date is not in the past
            if date < timezone.now().date():
                raise forms.ValidationError('You cannot create time slots in the past.')
            
            # Check if time slot is during business hours (9 AM to 5 PM)
            if start_time.hour < 9 or end_time.hour > 17:
                raise forms.ValidationError('Time slots must be between 9:00 AM and 5:00 PM.')
        
        return cleaned_data


# Update the CalendarAppointmentForm:
class CalendarAppointmentForm(forms.Form):
    """Form for booking an appointment from a calendar selection"""
    time_slot_id = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.CharField(
        label="Reason for appointment (optional)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Optional: Describe the reason for your appointment'}),
        required=False,
        help_text="You can leave this blank if you prefer"
    )


    
    def clean_time_slot_id(self):
        time_slot_id = self.cleaned_data.get('time_slot_id')
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id, is_booked=False)
            # Make sure the slot is not in the past
            if time_slot.date < timezone.now().date():
                raise forms.ValidationError("This time slot is no longer available.")
            # Store the time_slot for later use
            self.time_slot = time_slot
            return time_slot_id
        except TimeSlot.DoesNotExist:
            raise forms.ValidationError("The selected time slot is not available.")


# In appointments/forms.py, add:

class CancellationForm(forms.Form):
    """Form for providing a reason when cancelling an appointment"""
    cancellation_reason = forms.CharField(
        label="Reason for cancellation (optional)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text="You can leave this blank if you prefer"
    )
    

class CounselorAvailabilityForm(forms.Form):
    """Form for counselors to add multiple time slots at once"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select a date for the time slots"
    )
    start_hour = forms.IntegerField(
        min_value=9, max_value=16,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Starting hour (9-16, 24-hour format)"
    )
    end_hour = forms.IntegerField(
        min_value=10, max_value=17,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Ending hour (10-17, 24-hour format)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_hour = cleaned_data.get('start_hour')
        end_hour = cleaned_data.get('end_hour')
        
        if date and start_hour is not None and end_hour is not None:
            # Check that end hour is after start hour
            if start_hour >= end_hour:
                raise forms.ValidationError('End hour must be after start hour.')
            
            # Check that date is not in the past
            if date < timezone.now().date():
                raise forms.ValidationError('You cannot create time slots in the past.')
            
            # Check if hours are during business hours (9 AM to 5 PM)
            if start_hour < 9 or end_hour > 17:
                raise forms.ValidationError('Time slots must be between 9:00 AM and 5:00 PM.')
        
        return cleaned_data
    
    def save(self, counselor):
        """Create time slots for each hour in the specified range"""
        date = self.cleaned_data['date']
        start_hour = self.cleaned_data['start_hour']
        end_hour = self.cleaned_data['end_hour']
        
        created_slots = []
        for hour in range(start_hour, end_hour):
            # Create a time slot for this hour
            start_time = datetime.time(hour, 0)
            end_time = datetime.time(hour + 1, 0)
            
            # Check if a slot already exists
            existing_slot = TimeSlot.objects.filter(
                counselor=counselor,
                date=date,
                start_time=start_time,
                end_time=end_time
            ).first()
            
            if not existing_slot:
                slot = TimeSlot.objects.create(
                    counselor=counselor,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    is_booked=False
                )
                created_slots.append(slot)
        
        return created_slots