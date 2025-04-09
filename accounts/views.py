from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
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
    return render(request, 'accounts/home.html')

@login_required
@user_type_required(['counselor']) 

def counselor_dashboard(request):
    today = timezone.now().date()

    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        counselor=request.user,
        date_time__date__gte=today,
        status='scheduled'
    ).order_by('date_time')
    
    # Get past appointments
    past_appointments = Appointment.objects.filter(
        counselor=request.user,
        date_time__date__lt=today
    ).order_by('-date_time')
    
    # Get appointment stats
    total_appointments = Appointment.objects.filter(counselor=request.user).count()
    completed_appointments = Appointment.objects.filter(counselor=request.user, status='completed').count()
    cancelled_appointments = Appointment.objects.filter(counselor=request.user, status='cancelled').count()
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    return render(request, 'accounts/counselor_dashboard.html', context)



def profile(request):
    # Get user's appointments if they exist
    user_appointments = Appointment.objects.filter(user=request.user).order_by('date_time')
    
    # If the user is a counselor, also get appointments where they are the counselor
    counselor_appointments = None
    if request.user.user_type == 'counselor':
        counselor_appointments = Appointment.objects.filter(counselor=request.user).order_by('date_time')
    
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