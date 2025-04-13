from django import forms
from allauth.account.forms import SignupForm
from .models import User
from django.core.exceptions import ValidationError

class CustomSignupForm(SignupForm):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    )
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True,
                                 label="I am a",
                                 widget=forms.RadioSelect)
    phone_number = forms.CharField(max_length=15, required=False, 
                                 label="Phone Number (optional)")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('@')[1]
        
        allowed_domains = ['ucentralasia.org']
        if domain not in allowed_domains:
            raise forms.ValidationError(
                "Please use your UCA email address (@ucentralasia.org) to register."
            )
        return email
    
    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user