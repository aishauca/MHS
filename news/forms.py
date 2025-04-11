from django import forms
from .models import Event, EventRegistration

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'location', 'registration_required', 
                 'max_participants', 'image']
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        from django.utils import timezone
        
        if event_date and event_date < timezone.now():
            raise forms.ValidationError("Event date cannot be in the past.")
        
        return event_date
    
    def clean_max_participants(self):
        max_participants = self.cleaned_data.get('max_participants')
        registration_required = self.cleaned_data.get('registration_required')
        
        if registration_required and max_participants < 0:
            raise forms.ValidationError("Maximum participants cannot be negative.")
        
        return max_participants

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['additional_info']
        widgets = {
            'additional_info': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Optional: Any additional information you\'d like to provide?'}
            ),
        }