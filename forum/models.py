# forum/models.py

from typing import ClassVar

import bleach
import pytz  # Import pytz for timezone handling
from django.contrib.auth.models import User  # Import Django's built-in User model
from django.db import models

from categories.models import Category


# Profile model for extended user information
class Profile(models.Model):
    # Core relationship with User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Personal information fields
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Upload your avatar image",
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)

    # Forum-specific fields
    signature = models.TextField(blank=True)
    user_title = models.CharField(max_length=100, blank=True)

    # Contact/social media fields
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)

    # Preferences & settings
    # Generate timezone choices from pytz
    TIMEZONE_CHOICES: ClassVar = [(tz, tz) for tz in pytz.common_timezones]
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default="UTC")

    VISIBILITY_CHOICES = [  # noqa: RUF012
        ("public", "Public"),
        ("members", "Members Only"),
        ("hidden", "Hidden"),
    ]
    profile_visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
    )

    # Email notification preferences
    notify_on_reply = models.BooleanField(default=True)
    receive_newsletter = models.BooleanField(default=True)

    # Activity tracking
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        """Returns the URL of the user's avatar or a default avatar if none is set."""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        # Return a default avatar URL
        return "/static/forum/images/default_avatar.png"

    def get_sanitized_signature(self):
        """Returns the user's signature with HTML sanitized to prevent XSS attacks."""
        if not self.signature:
            return ""

        # Define allowed tags and attributes
        allowed_tags = [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "strong",
            "ul",
            "p",
            "br",
        ]
        allowed_attrs = {
            "a": ["href", "title"],
            "abbr": ["title"],
            "acronym": ["title"],
        }

        # Clean the signature using bleach
        clean_signature = bleach.clean(
            self.signature,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,
        )

        return clean_signature


# Create your models here.
# Model for a discussion topic/thread
class Topic(models.Model):
    subject = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        related_name="topics",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_sticky = models.BooleanField(default=False)  # Add this line for sticky topics
    category = models.ForeignKey(
        Category,
        related_name="topics",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    # We might add a 'last_updated' field later if needed

    # This helps represent the object nicely, e.g., in the admin area
    def __str__(self):
        return self.subject


# Model for a post/reply within a topic
class Post(models.Model):
    message = models.TextField()
    topic = models.ForeignKey(Topic, related_name="posts", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        User,
        related_name="posts_created",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
    )  # Field to store last update time

    # We could add 'updated_at' and 'updated_by' if we implement editing

    # This provides a readable representation of the Post object
    def __str__(self):
        # Show first 50 characters of the message
        return self.message[:50] + ("..." if len(self.message) > 50 else "")
