from django import forms
from allauth.account.forms import SignupForm
from .models import User

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
    
    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user