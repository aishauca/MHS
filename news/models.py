from django.db import models
from django.utils.text import slugify
from accounts.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    registration_required = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        from django.utils import timezone
        return self.event_date < timezone.now()
    
    @property
    def registration_count(self):
        return self.registrations.count()
    
    @property
    def has_space(self):
        if self.max_participants == 0:  # Unlimited
            return True
        return self.registration_count < self.max_participants


    @property
    def has_space(self):
        if self.max_participants == 0:  # Unlimited
            return True
        return self.registration_count < self.max_participants
        
    def get_related_upcoming_events(self):
        """Get other upcoming events (excluding this one)"""
        from django.utils import timezone
        return Event.objects.filter(
            event_date__gte=timezone.now()
        ).exclude(id=self.id).order_by('event_date')[:3]

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    additional_info = models.TextField(blank=True, null=True, help_text="Any additional information provided by the user")
    
    class Meta:
        unique_together = ['event', 'user']  # Prevent duplicate registrations
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"