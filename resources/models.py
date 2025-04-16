from django.db import models
from django.utils.text import slugify
from accounts.models import User

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Resource Categories"

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('article', 'Article'),
        ('pdf', 'PDF Document'),
        ('video', 'Video'),
        ('link', 'External Link'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    content = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ResourceFavorite(models.Model):
    """Model to track user's favorite resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_resources')
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'resource']
        
    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"