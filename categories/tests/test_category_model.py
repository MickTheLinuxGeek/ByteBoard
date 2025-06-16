from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from categories.models import Category
from forum.models import Topic


class TestCategoryModel(TestCase):
    """Tests for the Category model."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name="Test Category",
            description="This is a test category",
        )

        # Create a user for Topic tests
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

    def test_category_creation(self):
        """Test that a category is created correctly."""
        assert self.category.name == "Test Category"
        assert self.category.slug == "test-category"
        assert self.category.description == "This is a test category"

        # Test that created_at and updated_at are set
        assert self.category.created_at is not None
        assert self.category.updated_at is not None

        # Test string representation
        assert str(self.category) == "Test Category"

    def test_category_unique_name(self):
        """Test that category names must be unique."""
        # Try to create another category with the same name
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name="Test Category",
                description="This is another test category",
            )

    def test_category_unique_slug(self):
        """Test that category slugs must be unique."""
        # Try to create another category with a different name but same slug
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name="Test category",  # Different case but will generate same slug
                description="This is another test category",
            )

    def test_slug_generation(self):
        """Test that slugs are generated correctly from the name."""
        # Test with a simple name
        category = Category.objects.create(
            name="Simple Name",
            description="A category with a simple name",
        )
        assert category.slug == "simple-name"

        # Test with a name containing special characters
        category = Category.objects.create(
            name="Special & Characters!",
            description="A category with special characters",
        )
        assert category.slug == "special-characters"

        # Test with a very long name
        long_name = "This is a very long category name that should be properly slugified"
        category = Category.objects.create(
            name=long_name,
            description="A category with a long name",
        )
        assert category.slug == slugify(long_name)

    def test_manual_slug(self):
        """Test that a manually provided slug is not overwritten."""
        category = Category.objects.create(
            name="Manual Slug Test",
            slug="custom-slug",
            description="A category with a manually set slug",
        )
        assert category.slug == "custom-slug"

        # Test that the slug doesn't change when the name is updated
        category.name = "Updated Name"
        category.save()
        assert category.slug == "custom-slug"

    def test_topic_category_relationship(self):
        """Test the relationship between Topic and Category."""
        # Create a topic with the category
        topic = Topic.objects.create(
            subject="Test Topic",
            created_by=self.user,
            category=self.category,
        )

        # Test that the topic is associated with the category
        assert topic.category == self.category

        # Test that the category can access its topics
        assert self.category.topics.count() == 1
        assert self.category.topics.first() == topic

        # Test that multiple topics can be associated with a category
        topic2 = Topic.objects.create(
            subject="Another Test Topic",
            created_by=self.user,
            category=self.category,
        )
        assert self.category.topics.count() == 2

        # Test that topics remain when category is deleted (SET_NULL behavior)
        category_id = self.category.id
        self.category.delete()

        # Refresh topics from database
        topic.refresh_from_db()
        topic2.refresh_from_db()

        # Topics should still exist but have null category
        assert Topic.objects.filter(id=topic.id).exists()
        assert Topic.objects.filter(id=topic2.id).exists()
        assert topic.category is None
        assert topic2.category is None
