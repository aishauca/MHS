from django.contrib import admin
from .models import Appointment, AppointmentReminder

class AppointmentReminderInline(admin.TabularInline):
    model = AppointmentReminder
    extra = 0

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'counselor', 'date_time', 'status')
    list_filter = ('status', 'date_time')
    search_fields = ('user__username', 'counselor__username')
    inlines = [AppointmentReminderInline]