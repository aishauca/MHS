from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.http import JsonResponse
from .models import Event, EventRegistration
from .forms import EventForm, EventRegistrationForm
from accounts.views import user_type_required

# Custom permission check for counselors and admin staff
def is_counselor_or_admin(user):
    return user.is_superuser or user.user_type == 'counselor'

# Event views
@login_required
def event_list(request):
    """View to list all events"""
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    past_events = Event.objects.filter(event_date__lt=timezone.now()).order_by('-event_date')
    
    # For each event, check if the current user is registered
    for event in upcoming_events:
        event.is_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    }
    return render(request, 'news/event_list.html', context)

@login_required
def event_detail(request, slug):
    """View to display a specific event"""
    event = get_object_or_404(Event, slug=slug)
    
    # Check if user is registered for this event
    is_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()
    
    # Get registration count
    registration_count = EventRegistration.objects.filter(event=event).count()
    
    # Only counselors and admins can see the list of registrants
    registrants = None
    if is_counselor_or_admin(request.user):
        registrants = EventRegistration.objects.filter(event=event).select_related('user')
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'registration_count': registration_count,
        'registrants': registrants
    }
    return render(request, 'news/event_detail.html', context)

@login_required
def register_for_event(request, event_id):
    """View to register for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.info(request, f'You are already registered for "{event.title}".')
        return redirect('news:event_detail', slug=event.slug)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.save()
            messages.success(request, f'You have successfully registered for "{event.title}".')
            return redirect('news:event_detail', slug=event.slug)
    else:
        form = EventRegistrationForm()
    
    context = {
        'form': form,
        'event': event
    }
    return render(request, 'news/register_for_event.html', context)

@login_required
def unregister_from_event(request, event_id):
    """View to unregister from an event"""
    event = get_object_or_404(Event, id=event_id)
    registration = get_object_or_404(EventRegistration, event=event, user=request.user)
    
    if request.method == 'POST':
        registration.delete()
        messages.success(request, f'You have unregistered from "{event.title}".')
        return redirect('news:event_detail', slug=event.slug)
    
    context = {
        'event': event
    }
    return render(request, 'news/unregister_from_event.html', context)

# Counselor/Admin event management views
@login_required
@user_passes_test(is_counselor_or_admin)
def manage_events(request):
    """View for counselors to manage events"""
    events = Event.objects.all().order_by('-event_date')
    
    # Add a registration count attribute to each event (not using the property)
    for event in events:
        # Store the count directly as a temporary attribute, not trying to set the property
        event.reg_count = EventRegistration.objects.filter(event=event).count()
    
    context = {
        'events': events
    }
    return render(request, 'news/manage_events.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def add_event(request):
    """View for counselors to add an event"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            if not event.slug:
                event.slug = slugify(event.title)
            event.save()
            messages.success(request, f'Event "{event.title}" added successfully!')
            return redirect('news:event_detail', slug=event.slug)
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': 'Add New Event'
    }
    return render(request, 'news/event_form.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def edit_event(request, event_id):
    """View for counselors to edit an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('news:event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Edit Event: {event.title}'
    }
    return render(request, 'news/event_form.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def delete_event(request, event_id):
    """View for counselors to delete an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted successfully!')
        return redirect('news:manage_events')
    
    context = {
        'event': event
    }
    return render(request, 'news/delete_event.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def event_participants(request, event_id):
    """View to display all participants for an event"""
    event = get_object_or_404(Event, id=event_id)
    registrants = EventRegistration.objects.filter(event=event).select_related('user')
    
    context = {
        'event': event,
        'registrants': registrants
    }
    return render(request, 'news/event_participants.html', context)