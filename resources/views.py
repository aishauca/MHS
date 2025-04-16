from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Resource, ResourceCategory, ResourceFavorite
from .forms import ResourceForm, ResourceCategoryForm
from accounts.views import user_type_required

# Custom permission check for counselors and admin staff
def is_counselor_or_admin(user):
    return user.is_superuser or user.user_type == 'counselor'


@login_required
@user_passes_test(is_counselor_or_admin)
def add_resource(request):
    """View for counselors to add a new resource"""
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save()
            messages.success(request, f'Resource "{resource.title}" added successfully!')
            return redirect('resources:resource_detail', slug=resource.slug)
    else:
        form = ResourceForm()
    
    context = {
        'form': form,
        'title': 'Add New Resource',
    }
    return render(request, 'resources/resource_form.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def edit_resource(request, resource_id):
    """View for counselors to edit an existing resource"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            resource = form.save()
            messages.success(request, f'Resource "{resource.title}" updated successfully!')
            return redirect('resources:resource_detail', slug=resource.slug)
    else:
        form = ResourceForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
        'title': f'Edit Resource: {resource.title}',
    }
    return render(request, 'resources/resource_form.html', context)


@login_required
@user_passes_test(is_counselor_or_admin)
def delete_resource(request, resource_id):
    """View for counselors to delete a resource"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'Resource "{title}" deleted successfully!')
        return redirect('resources:resource_list')
    
    context = {
        'resource': resource,
    }
    return render(request, 'resources/delete_resource.html', context)

@login_required
@user_passes_test(is_counselor_or_admin)
def add_category(request):
    """View for counselors to add a new resource category"""
    if request.method == 'POST':
        form = ResourceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('resources:category_list')
    else:
        form = ResourceCategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category',
    }
    return render(request, 'resources/category_form.html', context)


@login_required
@user_passes_test(is_counselor_or_admin)
def edit_category(request, category_id):
    """View for counselors to edit an existing category"""
    category = get_object_or_404(ResourceCategory, id=category_id)
    
    if request.method == 'POST':
        form = ResourceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('resources:category_list')
    else:
        form = ResourceCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Edit Category: {category.name}',
    }
    return render(request, 'resources/category_form.html', context)


@login_required
def resource_list(request):
    """View to list all resources, optionally filtered by category or search query"""
    categories = ResourceCategory.objects.all()
    
    # Get search query if any
    search_query = request.GET.get('search', '')
    
    # Get selected category if any
    category_id = request.GET.get('category')
    selected_category = None
    
    # Apply filters
    if search_query:
        # Search in title and description
        resources = Resource.objects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    elif category_id:
        try:
            selected_category = ResourceCategory.objects.get(id=category_id)
            resources = Resource.objects.filter(category=selected_category)
        except ResourceCategory.DoesNotExist:
            resources = Resource.objects.all()
    else:
        resources = Resource.objects.all()
    
    # Get user favorites if authenticated
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = ResourceFavorite.objects.filter(
            user=request.user
        ).values_list('resource_id', flat=True)
    
    context = {
        'resources': resources,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'resources/resource_list.html', context)

@login_required
def resource_detail(request, slug):
    """View to display a specific resource"""
    resource = get_object_or_404(Resource, slug=slug)
    
    # Check if resource is in user's favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = ResourceFavorite.objects.filter(
            user=request.user, 
            resource=resource
        ).exists()
    
    context = {
        'resource': resource,
        'is_favorite': is_favorite
    }
    return render(request, 'resources/resource_detail.html', context)

@login_required
def category_list(request):
    """View to list all resource categories"""
    categories = ResourceCategory.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'resources/category_list.html', context)

@login_required
def download_resource(request, resource_id):
    """View to handle resource downloads"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Logic for handling resource downloads will go here
    # For files, redirect to the file URL
    if resource.file:
        return redirect(resource.file.url)
    # For external resources, redirect to the external URL
    elif resource.external_url:
        return redirect(resource.external_url)
    # For articles, redirect to the detail page
    else:
        return redirect('resources:resource_detail', slug=resource.slug)

@login_required
def toggle_favorite(request, resource_id):
    """Toggle a resource as favorite"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Check if resource is already favorited
    favorite, created = ResourceFavorite.objects.get_or_create(
        user=request.user,
        resource=resource
    )
    
    # If not created, it existed before, so we should delete it
    if not created:
        favorite.delete()
        is_favorite = False
        messages.success(request, f'"{resource.title}" removed from favorites!')
    else:
        is_favorite = True
        messages.success(request, f'"{resource.title}" added to favorites!')
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    # If not AJAX, redirect back
    return redirect('resources:resource_detail', slug=resource.slug)

@login_required
def favorite_resources(request):
    """View to display user's favorite resources"""
    favorites = ResourceFavorite.objects.filter(user=request.user).select_related('resource', 'resource__category')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'resources/favorite_resources.html', context)