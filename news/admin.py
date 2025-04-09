from django.contrib import admin
from .models import Event, NewsArticle

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location')
    list_filter = ('event_date',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}