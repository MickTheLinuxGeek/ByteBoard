from django.test import TestCase

from forum.forms import NewPostForm


class TestNewPostForm(TestCase):
    """Tests for the NewPostForm."""

    def test_form_valid_data(self):
        """Test that the form is valid with valid data."""
        form_data = {
            "message": "This is a test reply message.",
        }
        form = NewPostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_empty_message(self):
        """Test that the form is invalid with an empty message."""
        form_data = {
            "message": "",
        }
        form = NewPostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_form_whitespace_only_message(self):
        """Test that the form is invalid with a message containing only whitespace."""
        form_data = {
            "message": "   ",
        }
        form = NewPostForm(data=form_data)
        self.assertFalse(form.is_valid())  # Django's CharField validates whitespace-only as empty
        self.assertIn("message", form.errors)

        # Django's CharField treats whitespace-only input as empty by default
        # This is the expected behavior

    def test_form_very_long_message(self):
        """Test that the form handles very long messages correctly."""
        # Create a very long message (10,000 characters)
        long_message = "x" * 10000
        form_data = {
            "message": long_message,
        }
        form = NewPostForm(data=form_data)
        self.assertTrue(form.is_valid())  # Django's CharField doesn't have a max length by default

        # The view might need additional validation for very long messages
        # This test documents the current behavior
