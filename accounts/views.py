from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
from appointments.models import Appointment
from django.utils import timezone
from .forms import UserProfileForm

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
    return render(request, 'accounts/home.html')

# In accounts/views.py, update the counselor_dashboard view:


def home(request):
    # Get upcoming events
    from news.models import Event
    from django.utils import timezone
    
    upcoming_events = Event.objects.filter(
        event_date__gte=timezone.now()
    ).order_by('event_date')[:3]  # Get the 3 nearest upcoming events
    
    context = {
        'upcoming_events': upcoming_events
    }
    
    return render(request, 'accounts/home.html', context)

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

# Example of a restricted view
@login_required
@user_type_required(['counselor'])
def counselor_dashboard(request):
    # Only counselors can access this view
    appointments = Appointment.objects.filter(counselor=request.user).order_by('date_time')
    context = {
        'appointments': appointments,
    }
    return render(request, 'accounts/counselor_dashboard.html', context) 

# accounts/views.py
# Add this import

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