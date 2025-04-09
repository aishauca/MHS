from django.contrib import admin
from .models import ResourceCategory, Resource

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'category', 'created_at')
    list_filter = ('resource_type', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}