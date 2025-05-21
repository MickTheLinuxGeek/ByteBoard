# forum/models.py

from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model
from django.utils import timezone


# Create your models here.
# Model for a discussion topic/thread
class Topic(models.Model):
    subject = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sticky = models.BooleanField(default=False)  # Add this line for sticky topics

    # We might add a 'last_updated' field later if needed

    # This helps represent the object nicely, e.g., in the admin area
    def __str__(self):
        return self.subject


# Model for a post/reply within a topic
class Post(models.Model):
    message = models.TextField()
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='posts_created', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)  # Field to store last update time

    # We could add 'updated_at' and 'updated_by' if we implement editing

    # This provides a readable representation of the Post object
    def __str__(self):
        # Show first 50 characters of the message
        return self.message[:50] + ('...' if len(self.message) > 50 else '')
