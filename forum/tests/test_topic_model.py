from django.contrib.auth.models import User
from django.test import TestCase

from forum.models import Topic
from categories.models import Category


class TestTopicModel(TestCase):
    """Tests for the Topic model."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
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

    def test_topic_creation(self):
        """Test that a topic is created correctly."""
        assert self.topic.subject == "Test Topic"  # noqa: S101
        assert self.topic.created_by == self.user  # noqa: S101
        assert self.topic.category == self.category  # noqa: S101
        assert not self.topic.is_sticky  # noqa: S101
        assert self.topic.created_at is not None  # noqa: S101

    def test_topic_string_representation(self):
        """Test the string representation of a topic."""
        assert str(self.topic) == "Test Topic"  # noqa: S101

    def test_topic_sticky_flag(self):
        """Test that the sticky flag can be set and retrieved."""
        # Default is False
        assert not self.topic.is_sticky  # noqa: S101
        
        # Set to True
        self.topic.is_sticky = True
        self.topic.save()
        
        # Refresh from database
        self.topic.refresh_from_db()
        
        # Check that it's now True
        assert self.topic.is_sticky  # noqa: S101