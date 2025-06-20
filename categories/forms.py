# categories/forms.py

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from .models import Category


class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing categories.
    
    This form allows users to create new categories or edit existing ones.
    The slug field is automatically generated from the name if not provided.
    """
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Enter category name'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Describe the category'}
            ),
        }
        labels = {
            'name': 'Category Name',
            'description': 'Description',
        }
        help_texts = {
            'name': 'The name of the category. Must be unique.',
            'description': 'A brief description of what this category is about.',
        }
    
    def clean_name(self):
        """
        Validate that the category name is unique.
        """
        name = self.cleaned_data.get('name')
        
        # Check if a category with this name already exists
        # If we're editing an existing category, exclude the current instance
        if self.instance.pk:
            if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('A category with this name already exists.')
        else:
            if Category.objects.filter(name=name).exists():
                raise ValidationError('A category with this name already exists.')
        
        return name
    
    def save(self, commit=True):
        """
        Save the form and generate a slug from the name if not provided.
        """
        category = super().save(commit=False)
        
        # Generate slug from name if not provided
        if not category.slug:
            category.slug = slugify(category.name)
        
        if commit:
            category.save()
        
        return category