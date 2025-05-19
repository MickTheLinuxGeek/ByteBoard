# Register your models here.
# forum/admin.py

from django.contrib import admin
from .models import Topic, Post  # Import your models


# Basic registration (uncomment to see the default admin interface)
# admin.site.register(Topic)
# admin.site.register(Post)

# Customized Admin Interface for Topic model
@admin.register(Topic)  # Use decorator to register the model with its admin class
class TopicAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('subject', 'created_by', 'created_at')
    # Fields to allow searching by
    search_fields = ('subject', 'created_by__username')  # Search related User's username
    # Filters to add in the sidebar
    list_filter = ('created_at', 'created_by')
    # Add a date hierarchy navigation
    date_hierarchy = 'created_at'
    # Default ordering
    ordering = ('-created_at',)


# Customized Admin Interface for Post model
@admin.register(Post)  # Use decorator to register
class PostAdmin(admin.ModelAdmin):
    # Columns to display (using __str__ for a snippet of the message)
    list_display = ('__str__', 'topic', 'created_by', 'created_at')
    # Enable searching these fields
    search_fields = ('message', 'topic__subject', 'created_by__username')
    # Enable filtering
    list_filter = ('created_at', 'created_by', 'topic')
    # Add date hierarchy
    date_hierarchy = 'created_at'
    # Use raw_id_fields for ForeignKey fields with potentially many choices
    # This replaces dropdowns with a text input and a lookup popup
    raw_id_fields = ('topic', 'created_by')
    # Default ordering
    ordering = ('-created_at',)
