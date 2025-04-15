from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('counselor-dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # More URL patterns will be added later

    # Add this new URL pattern for the debug view
    path('debug/', views.debug_view, name='debug_view'),
]
