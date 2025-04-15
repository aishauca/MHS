from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class RegistrationForm(forms.ModelForm):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    )
    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True,
                                 label="I am a",
                                 widget=forms.RadioSelect)
    phone_number = forms.CharField(max_length=15, required=False, 
                                 label="Phone Number (optional)")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('@')[1]
        
        allowed_domains = ['ucentralasia.org']
        if domain not in allowed_domains:
            raise forms.ValidationError(
                "Please use your UCA email address (@ucentralasia.org) to register."
            )
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email address is already in use. Please use a different email or login to your existing account."
            )
            
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False  # User inactive until email verification
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')  # Change to EmailField
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('username')  # AuthenticationForm still calls it "username"
        password = self.cleaned_data.get('password')

        if email and password:
            # Authenticate directly with email
            self.user_cache = authenticate(
                self.request, username=email, password=password  # Django will use email as username
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'Email'},  # Change the message to refer to email
                )
            else:
                self.confirm_login_allowed(self.user_cache)
                
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the fields required except phone_number
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True