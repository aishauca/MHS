from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings
from datetime import timedelta
from functools import wraps

from .models import User, EmailVerificationToken
from .forms import RegistrationForm, CustomLoginForm, UserProfileForm
from appointments.models import Appointment

def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.user_type in allowed_types:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

def home(request):
    # Get upcoming events
    from news.models import Event
    
    upcoming_events = Event.objects.filter(
        event_date__gte=timezone.now()
    ).order_by('event_date')[:3]  # Get the 3 nearest upcoming events
    
    context = {
        'upcoming_events': upcoming_events
    }
    
    return render(request, 'accounts/home.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create verification token
            token = EmailVerificationToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(days=3)
            )
            
            # Build verification URL
            verify_url = request.build_absolute_uri(
                reverse('accounts:verify_email', args=[token.token])
            )
            
            # Send verification email
            subject = "Verify your UCA Mental Health account"
            html_message = render_to_string('accounts/email/verification_email.html', {
                'user': user,
                'verify_url': verify_url,
                'expiry_days': 3,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Redirect to verification sent page
            request.session['verification_email'] = user.email
            return redirect('accounts:verification_sent')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verification_sent(request):
    verification_email = request.session.get('verification_email', '')
    return render(request, 'accounts/verification_sent.html', {
        'verification_email': verification_email
    })

def verify_email(request, token):
    try:
        verification_token = get_object_or_404(EmailVerificationToken, token=token)
        
        if not verification_token.is_valid():
            return render(request, 'accounts/verification_expired.html')
        
        user = verification_token.user
        user.is_active = True
        user.save()
        
        # Delete the token so it can't be used again
        verification_token.delete()
        
        # Log the user in
        login(request, user)
        
        messages.success(request, "Your email has been verified and your account is now active!")
        return redirect('accounts:profile')
    except Exception as e:
        # Log the error for debugging
        print(f"Error in verify_email: {e}")
        # Provide a helpful error page
        return render(request, 'accounts/verification_error.html', {'error': str(e)})


 
def delete_profile(request):
    """View for users to delete their own profile"""
    if request.method == 'POST':
        user = request.user
        # Log the user out
        logout(request)
        # Delete the user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('accounts:home')
    
    return render(request, 'accounts/delete_profile.html')       

def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get('next', 'accounts:profile')
                    return redirect(next_url)
                else:
                    messages.error(request, "Your account is not active. Please check your email for the verification link.")
                    return redirect('accounts:account_inactive')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('accounts:home')
    return render(request, 'accounts/logout.html')

def account_inactive(request):
    return render(request, 'accounts/account_inactive.html')

@login_required
def profile(request):
    # Get only the user's upcoming appointments
    user_appointments = Appointment.objects.filter(
        user=request.user,
        date_time__gte=timezone.now(),
        status='scheduled'
    ).order_by('date_time')
    
    # If the user is a counselor, also get appointments where they are the counselor
    counselor_appointments = None
    if request.user.user_type == 'counselor':
        counselor_appointments = Appointment.objects.filter(
            counselor=request.user,
            date_time__gte=timezone.now(),
            status='scheduled'
        ).order_by('date_time')
    
    context = {
        'user': request.user,
        'user_appointments': user_appointments,
        'counselor_appointments': counselor_appointments,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@user_type_required(['counselor'])
def counselor_dashboard(request):
    """Dashboard for counselors to manage appointments and availability"""
    # Get current date and time
    now = timezone.now()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        counselor=request.user,
        date_time__gte=now,
        status='scheduled'
    ).order_by('date_time')
    
    # Get past appointments
    past_appointments = Appointment.objects.filter(
        counselor=request.user,
        date_time__lt=now
    ).order_by('-date_time')
    
    # Get canceled appointments
    cancelled_appointments = Appointment.objects.filter(
        counselor=request.user,
        status='cancelled'
    ).order_by('-date_time')
    
    # Get appointment stats
    total_appointments = Appointment.objects.filter(counselor=request.user).count()
    completed_appointments = Appointment.objects.filter(counselor=request.user, status='completed').count()
    cancelled_count = Appointment.objects.filter(counselor=request.user, status='cancelled').count()
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments_count': cancelled_count,
    }
    return render(request, 'accounts/counselor_dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)

# Debug view
def debug_view(request):
    origin = request.META.get('HTTP_ORIGIN', 'No origin')
    referer = request.META.get('HTTP_REFERER', 'No referer')
    host = request.META.get('HTTP_HOST', 'No host')
    return HttpResponse(f"Origin: {origin}<br>Referer: {referer}<br>Host: {host}")

@user_passes_test(lambda u: u.is_superuser)
def debug_email_verification(request):
    """Debug view to show all unverified email addresses. Only for superusers."""
    unverified_users = User.objects.filter(is_active=False)
    active_users = User.objects.filter(is_active=True)
    verification_tokens = EmailVerificationToken.objects.all()
    
    context = {
        'unverified_users': unverified_users,
        'active_users': active_users,
        'verification_tokens': verification_tokens,
    }
    return render(request, 'accounts/debug_email_verification.html', context)