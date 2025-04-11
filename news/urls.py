from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Event views for all users
    path('events/', views.event_list, name='event_list'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/unregister/', views.unregister_from_event, name='unregister_from_event'),
    
    # Event management for counselors/admins
    path('manage/events/', views.manage_events, name='manage_events'),
    path('manage/events/add/', views.add_event, name='add_event'),
    path('manage/events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('manage/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('manage/events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
    
    # Default path - redirect to events
    path('', views.event_list, name='index'),
]