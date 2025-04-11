from django.contrib import admin
from .models import Event, EventRegistration

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ('registration_date',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'registration_required', 'registration_count', 'is_past')
    list_filter = ('event_date', 'registration_required')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EventRegistrationInline]
    
    def registration_count(self, obj):
        return obj.registrations.count()
    
    registration_count.short_description = 'Registrations'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registration_date')
    list_filter = ('registration_date', 'event')
    search_fields = ('user__username', 'user__email', 'event__title')
    readonly_fields = ('registration_date',)