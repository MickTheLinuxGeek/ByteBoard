# Register your models here.
# forum/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Post, Profile, Topic  # Import your models


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


# Inline admin for Profile model within User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


# Customized Admin Interface for Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "user_title", "profile_visibility", "last_seen")
    search_fields = ("user__username", "user__email", "location", "bio")
    list_filter = ("profile_visibility", "notify_on_reply", "receive_newsletter")
    raw_id_fields = ("user",)
    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        ("Personal Information", {"fields": ("avatar", "bio", "location", "birth_date", "website")}),
        ("Forum Information", {"fields": ("signature", "user_title")}),
        ("Social Media", {"fields": ("twitter", "github", "linkedin")}),
        ("Preferences", {"fields": ("timezone", "profile_visibility", "notify_on_reply", "receive_newsletter")}),
        ("Activity", {"fields": ("last_seen",)}),
    )
    readonly_fields = ("last_seen",)


# Extend the default UserAdmin to include ProfileInline
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
