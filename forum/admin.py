# Register your models here.
# forum/admin.py

from django.contrib import admin

from .models import Post, Topic  # Import your models


# Basic registration (uncomment to see the default admin interface)
# admin.site.register(Topic)
# admin.site.register(Post)

# Customized Admin Interface for Topic model

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("subject", "created_by", "created_at", "is_sticky")  # Add 'is_sticky'
    search_fields = ("subject", "created_by__username")
    list_filter = ("created_at", "created_by", "is_sticky")  # Add 'is_sticky'
    date_hierarchy = "created_at"
    ordering = ("-is_sticky", "-created_at")  # Order by sticky status first, then by date
    list_editable = ("is_sticky",)  # Allow editing sticky status directly in the list view


# Customized Admin Interface for Post model
@admin.register(Post)  # Use decorator to register
class PostAdmin(admin.ModelAdmin):
    # Columns to display (using __str__ for a snippet of the message)
    list_display = ("__str__", "topic", "created_by", "created_at")
    # Enable searching these fields
    search_fields = ("message", "topic__subject", "created_by__username")
    # Enable filtering
    list_filter = ("created_at", "created_by", "topic")
    # Add date hierarchy
    date_hierarchy = "created_at"
    # Use raw_id_fields for ForeignKey fields with potentially many choices
    # This replaces dropdowns with a text input and a lookup popup
    raw_id_fields = ("topic", "created_by")
    # Default ordering
    ordering = ("-created_at",)
