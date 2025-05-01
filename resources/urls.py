from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Admin URLs for managing resources - these need to come BEFORE the slug pattern
   # Add to resources/urls.py near the top of urlpatterns:
    path('safe-test/', views.safe_test, name='safe_test'),
    path('add/', views.add_resource, name='add_resource'),
    path('edit/<int:resource_id>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    
    path('favorite/<int:resource_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_resources, name='favorite_resources'),
    # These should come after the more specific patterns
    path('', views.resource_list, name='resource_list'),
    path('categories/', views.category_list, name='category_list'),
    path('download/<int:resource_id>/', views.download_resource, name='download_resource'),
    
    # The catch-all slug pattern must be last
    path('<slug:slug>/', views.resource_detail, name='resource_detail'),


    

]