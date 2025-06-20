from django.contrib.auth.models import User
from django.test import TestCase

from forum.forms import NewTopicForm
from categories.models import Category


class TestNewTopicForm(TestCase):
    """Tests for the NewTopicForm."""

    def setUp(self):
        """Set up test data."""
        # Create a test category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description",
        )

    def test_form_valid_data(self):
        """Test that the form is valid with valid data."""
        form_data = {
            "subject": "Test Topic",
            "category": self.category.id,
            "message": "This is a test message for the topic.",
        }
        form = NewTopicForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_empty_subject(self):
        """Test that the form is invalid with an empty subject."""
        form_data = {
            "subject": "",
            "category": self.category.id,
            "message": "This is a test message for the topic.",
        }
        form = NewTopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)

    def test_form_empty_message(self):
        """Test that the form is invalid with an empty message."""
        form_data = {
            "subject": "Test Topic",
            "category": self.category.id,
            "message": "",
        }
        form = NewTopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_form_no_category(self):
        """Test that the form is invalid without a category."""
        form_data = {
            "subject": "Test Topic",
            "message": "This is a test message for the topic.",
        }
        form = NewTopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_form_invalid_category(self):
        """Test that the form is invalid with an invalid category ID."""
        # Use a non-existent category ID
        form_data = {
            "subject": "Test Topic",
            "category": 999,  # Non-existent ID
            "message": "This is a test message for the topic.",
        }
        form = NewTopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_form_long_subject(self):
        """Test that the form is invalid with a subject that's too long."""
        # Create a subject that's longer than the max length (255 characters)
        long_subject = "x" * 256
        form_data = {
            "subject": long_subject,
            "category": self.category.id,
            "message": "This is a test message for the topic.",
        }
        form = NewTopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)