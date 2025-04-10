from django import forms
from .models import Resource, ResourceCategory

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'content', 'resource_type', 'category', 'file', 'external_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        file = cleaned_data.get('file')
        external_url = cleaned_data.get('external_url')
        
        # Validate based on resource type
        if resource_type == 'pdf' and not file:
            self.add_error('file', 'PDF resources must have a file uploaded.')
        elif resource_type == 'link' and not external_url:
            self.add_error('external_url', 'External link resources must have a URL.')
        
        return cleaned_data

class ResourceCategoryForm(forms.ModelForm):
    class Meta:
        model = ResourceCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }