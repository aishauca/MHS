from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('account-inactive/', views.account_inactive, name='account_inactive'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('counselor-dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    # Password reset URLs - Use Django's built-in views
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/email/password_reset_email.html',
             html_email_template_name='accounts/email/password_reset_email.html',
             subject_template_name='accounts/email/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'

         ), 
         name='password_reset'),


    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
         
    # Debug views
    path('debug/', views.debug_view, name='debug_view'),
    path('debug-email-verification/', views.debug_email_verification, name='debug_email_verification'),
]