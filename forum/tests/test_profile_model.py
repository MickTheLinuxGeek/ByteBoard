# import pytest
# from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.test import TestCase

from forum.models import Profile


class TestProfileModel(TestCase):
    """Tests for the Profile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_creation(self):
        """Test that a profile is created correctly."""
        assert self.profile.user == self.user  # noqa: S101
        assert str(self.profile) == "testuser's profile"  # noqa: S101

        # Test default values
        assert self.profile.timezone == "UTC"  # noqa: S101
        assert self.profile.profile_visibility == "public"  # noqa: S101
        assert self.profile.notify_on_reply  # noqa: S101
        assert self.profile.receive_newsletter  # noqa: S101

        # Test empty fields
        assert self.profile.bio == ""  # noqa: S101
        assert self.profile.location == ""  # noqa: S101
        assert self.profile.birth_date is None  # noqa: S101
        assert self.profile.website == ""  # noqa: S101
        assert self.profile.signature == ""  # noqa: S101
        assert self.profile.user_title == ""  # noqa: S101
        assert self.profile.twitter == ""  # noqa: S101
        assert self.profile.github == ""  # noqa: S101
        assert self.profile.linkedin == ""  # noqa: S101
        assert self.profile.last_seen is None  # noqa: S101

    def test_profile_update(self):
        """Test that a profile can be updated."""
        self.profile.bio = "Test bio"
        self.profile.location = "Test location"
        self.profile.save()

        # Refresh from database
        self.profile.refresh_from_db()

        assert self.profile.bio == "Test bio"  # noqa: S101
        assert self.profile.location == "Test location"  # noqa: S101

    def test_get_avatar_url_default(self):
        """Test that get_avatar_url returns the default avatar URL when no avatar is set."""
        assert (  # noqa: S101
            self.profile.get_avatar_url() == "/static/forum/images/default_avatar.png"
        )

    def test_get_sanitized_signature_empty(self):
        """Test that get_sanitized_signature returns an empty string when no signature is set."""
        assert self.profile.get_sanitized_signature() == ""  # noqa: S101

    def test_get_sanitized_signature_with_content(self):
        """Test that get_sanitized_signature sanitizes HTML in the signature."""
        # Set a signature with some HTML
        self.profile.signature = "<p>Test signature</p><script>alert('XSS');</script>"
        self.profile.save()

        # The script tag should be removed
        sanitized = self.profile.get_sanitized_signature()
        assert "<p>Test signature</p>" in sanitized  # noqa: S101
        # Check that the script tag is removed, but don't check for the content
        # as bleach might handle it differently
        assert "<script>" not in sanitized  # noqa: S101
