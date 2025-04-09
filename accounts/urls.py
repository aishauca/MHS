from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('counselor-dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    # More URL patterns will be added later
]
