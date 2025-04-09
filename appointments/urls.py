from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Keep the view, cancel, complete functionality
    path('view/<int:appointment_id>/', views.view_appointment, name='view_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    
    # Calendar testing and views
    path('calendar-test/', views.calendar_test, name='calendar_test'),
    path('counselor-calendar/', views.counselor_calendar, name='counselor_calendar'),
    path('booking-calendar/', views.booking_calendar, name='booking_calendar'),
    
    # New calendar-based booking functionality
    path('slot/<int:slot_id>/book/', views.create_appointment_from_slot, name='create_appointment_from_slot'),
    path('time-slots/add-multiple/', views.add_multiple_time_slots, name='add_multiple_slots'),
    
    # Time slot management
    path('time-slots/', views.manage_time_slots, name='manage_time_slots'),
    path('time-slots/add/', views.add_time_slot, name='add_time_slot'),
    path('time-slots/delete/<int:slot_id>/', views.delete_time_slot, name='delete_time_slot'),
    
    # API endpoints for calendar data
    path('api/slots/counselor/<int:counselor_id>/', views.get_counselor_slots, name='get_counselor_slots'),
    path('api/slots/counselor/', views.get_counselor_slots, name='get_own_slots'),
    path('api/slots/available/', views.get_available_slots, name='get_available_slots'),
]