from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from forum.models import Post, Topic
from categories.models import Category


class TestPostModel(TestCase):
    """Tests for the Post model."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        
        # Create another test user for testing different creators
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpassword",  # noqa: S106
        )
        
        # Create a test category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description",
        )
        
        # Create a test topic
        self.topic = Topic.objects.create(
            subject="Test Topic",
            created_by=self.user,
            category=self.category,
        )
        
        # Create a test post
        self.post = Post.objects.create(
            message="Test message content",
            topic=self.topic,
            created_by=self.user,
        )

    def test_post_creation(self):
        """Test that a post is created correctly."""
        assert self.post.message == "Test message content"  # noqa: S101
        assert self.post.topic == self.topic  # noqa: S101
        assert self.post.created_by == self.user  # noqa: S101
        assert self.post.created_at is not None  # noqa: S101
        assert self.post.updated_at is None  # noqa: S101

    def test_post_string_representation(self):
        """Test the string representation of a post."""
        assert str(self.post) == "Test message content"  # noqa: S101
        
        # Test with a long message (over 50 characters)
        long_message = "This is a very long message that should be truncated in the string representation of the post object."
        long_post = Post.objects.create(
            message=long_message,
            topic=self.topic,
            created_by=self.user,
        )
        assert str(long_post) == long_message[:50] + "..."  # noqa: S101

    def test_post_update(self):
        """Test that a post can be updated."""
        # Update the message
        self.post.message = "Updated message content"
        self.post.updated_at = timezone.now()
        self.post.save()
        
        # Refresh from database
        self.post.refresh_from_db()
        
        # Check that the message was updated
        assert self.post.message == "Updated message content"  # noqa: S101
        assert self.post.updated_at is not None  # noqa: S101

    def test_post_by_different_user(self):
        """Test that a post can be created by a different user."""
        # Create a post by a different user
        other_post = Post.objects.create(
            message="Message from another user",
            topic=self.topic,
            created_by=self.other_user,
        )
        
        # Check that the post was created correctly
        assert other_post.message == "Message from another user"  # noqa: S101
        assert other_post.topic == self.topic  # noqa: S101
        assert other_post.created_by == self.other_user  # noqa: S101
        assert other_post.created_at is not None  # noqa: S101