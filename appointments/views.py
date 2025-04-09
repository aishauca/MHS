import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Appointment, TimeSlot
from accounts.models import User
from accounts.views import user_type_required
from .forms import AppointmentForm, TimeSlotForm, CalendarAppointmentForm, CounselorAvailabilityForm

@login_required
def view_appointment(request, appointment_id):
    """View details of a specific appointment"""
    # Get the appointment, ensuring the user has permission
    if request.user.user_type == 'counselor':
        appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/view_appointment.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Allow users or counselors to cancel an appointment"""
    # Get the appointment, ensuring the user has permission
    if request.user.user_type == 'counselor':
        appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        
        # If there's a time slot linked to this appointment, mark it as available again
        try:
            time_slot = TimeSlot.objects.get(appointment=appointment)
            time_slot.is_booked = False
            time_slot.appointment = None
            time_slot.save()
        except TimeSlot.DoesNotExist:
            pass
            
        messages.success(request, 'Appointment cancelled successfully.')
        
        if request.user.user_type == 'counselor':
            return redirect('accounts:counselor_dashboard')
        else:
            return redirect('accounts:profile')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/cancel_appointment.html', context)

@login_required
@user_type_required(['counselor'])
def complete_appointment(request, appointment_id):
    """Allow counselors to mark an appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id, counselor=request.user)
    
    if request.method == 'POST':
        appointment.status = 'completed'
        appointment.save()
        messages.success(request, 'Appointment marked as completed.')
        return redirect('accounts:counselor_dashboard')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/complete_appointment.html', context)

@login_required
def my_appointments(request):
    """View all appointments for the logged-in user"""
    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        date_time__gte=timezone.now(),
    ).order_by('date_time')
    
    past_appointments = Appointment.objects.filter(
        user=request.user,
        date_time__lt=timezone.now(),
    ).order_by('-date_time')
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'appointments/my_appointments.html', context)

# Calendar-based appointment booking views
@login_required
def booking_calendar(request):
    """Calendar view for users to book appointments"""
    # Get all counselors
    counselors = User.objects.filter(user_type='counselor')
    
    context = {
        'counselors': counselors
    }
    return render(request, 'appointments/booking_calendar.html', context)

@login_required
def create_appointment_from_slot(request, slot_id):
    """Create an appointment from a selected time slot"""
    # Get the time slot
    time_slot = get_object_or_404(TimeSlot, id=slot_id, is_booked=False)
    
    if request.method == 'POST':
        form = CalendarAppointmentForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            
            # Create the appointment
            appointment = Appointment.objects.create(
                user=request.user,
                counselor=time_slot.counselor,
                date_time=datetime.datetime.combine(time_slot.date, time_slot.start_time),
                reason=reason,
                status='scheduled'
            )
            
            # Mark the time slot as booked and link to appointment
            time_slot.is_booked = True
            time_slot.appointment = appointment
            time_slot.save()
            
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('accounts:profile')
    else:
        form = CalendarAppointmentForm(initial={'time_slot_id': slot_id})
    
    context = {
        'form': form,
        'time_slot': time_slot
    }
    return render(request, 'appointments/create_appointment.html', context)

# Counselor time slot management views
@login_required
@user_type_required(['counselor'])
def counselor_calendar(request):
    """Calendar view for counselors to manage their availability"""
    return render(request, 'appointments/counselor_calendar.html')

@login_required
@user_type_required(['counselor'])
def manage_time_slots(request):
    """Allow counselors to manage their available time slots"""
    time_slots = TimeSlot.objects.filter(counselor=request.user).order_by('date', 'start_time')
    
    context = {
        'time_slots': time_slots,
    }
    return render(request, 'appointments/manage_time_slots.html', context)

@login_required
@user_type_required(['counselor'])
def add_time_slot(request):
    """Allow counselors to add a single time slot"""
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.counselor = request.user
            time_slot.save()
            messages.success(request, 'Time slot added successfully!')
            return redirect('appointments:manage_time_slots')
    else:
        form = TimeSlotForm()
    
    context = {
        'form': form,
    }
    return render(request, 'appointments/add_time_slot.html', context)

@login_required
@user_type_required(['counselor'])
def add_multiple_time_slots(request):
    """Allow counselors to add multiple time slots at once"""
    if request.method == 'POST':
        form = CounselorAvailabilityForm(request.POST)
        if form.is_valid():
            slots = form.save(counselor=request.user)
            messages.success(request, f'{len(slots)} time slots added successfully!')
            return redirect('appointments:counselor_calendar')
    else:
        form = CounselorAvailabilityForm()
    
    context = {
        'form': form,
    }
    return render(request, 'appointments/add_multiple_slots.html', context)

@login_required
@user_type_required(['counselor'])
def delete_time_slot(request, slot_id):
    """Allow counselors to delete available time slots"""
    time_slot = get_object_or_404(TimeSlot, id=slot_id, counselor=request.user, is_booked=False)
    
    if request.method == 'POST':
        time_slot.delete()
        messages.success(request, 'Time slot deleted successfully!')
        return redirect('appointments:manage_time_slots')
    
    context = {
        'time_slot': time_slot,
    }
    return render(request, 'appointments/delete_time_slot.html', context)

# Testing view
def calendar_test(request):
    """Simple view to test the calendar functionality"""
    return render(request, 'appointments/calendar_test.html')

# API views for calendar data
@login_required
def get_counselor_slots(request, counselor_id=None):
    """Return time slots for a specific counselor in JSON format"""
    # If no counselor_id is provided and user is a counselor, show their own slots
    if counselor_id is None and request.user.user_type == 'counselor':
        counselor_id = request.user.id
        
    # Get slots for the counselor
    slots = TimeSlot.objects.filter(counselor_id=counselor_id)
    
    # Format slots for FullCalendar
    data = []
    for slot in slots:
        # Create datetime objects for start and end
        start_datetime = datetime.datetime.combine(slot.date, slot.start_time)
        end_datetime = datetime.datetime.combine(slot.date, slot.end_time)
        
        # Format in ISO format for FullCalendar
        data.append({
            'id': slot.id,
            'title': 'Booked' if slot.is_booked else 'Available',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'color': '#007bff' if slot.is_booked else '#28a745',  # Blue if booked, green if available
            'editable': not slot.is_booked,  # Only allow editing available slots
        })
    
    return JsonResponse(data, safe=False)

@login_required
def get_available_slots(request):
    """Return only available time slots in JSON format"""
    # Get all available slots
    slots = TimeSlot.objects.filter(is_booked=False, date__gte=timezone.now().date())
    
    # Format slots for FullCalendar
    data = []
    for slot in slots:
        counselor_name = slot.counselor.get_full_name() or slot.counselor.username
        
        # Create datetime objects for start and end
        start_datetime = datetime.datetime.combine(slot.date, slot.start_time)
        end_datetime = datetime.datetime.combine(slot.date, slot.end_time)
        
        # Format in ISO format for FullCalendar
        data.append({
            'id': slot.id,
            'title': f'Available with {counselor_name}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'color': '#28a745',  # Green for available
        })
    
    return JsonResponse(data, safe=False)