# import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from forum.models import Profile


class TestProfileSignals(TestCase):
    """Tests for the Profile signals."""

    def test_profile_created_on_user_creation(self):
        """Test that a profile is automatically created when a user is created."""
        # Create a user
        user = User.objects.create_user(
            username="signaltest",
            email="signal@example.com",
            password="signalpassword",  # noqa: S106
        )

        # Check that a profile was automatically created
        profile_exists = Profile.objects.filter(user=user).exists()
        assert profile_exists  # noqa: S101

        # Get the profile and check its properties
        profile = Profile.objects.get(user=user)
        assert profile.user == user  # noqa: S101
        assert str(profile) == "signaltest's profile"  # noqa: S101

    def test_profile_created_for_existing_user(self):
        """Test that a profile is created for an existing user when the user is saved."""
        # Create a user without triggering the signal (this is just for testing)
        user = User.objects.create(
            username="existinguser",
            email="existing@example.com",
        )
        user.set_password("existingpassword")

        # Delete the profile if it was created
        Profile.objects.filter(user=user).delete()

        # Verify no profile exists
        profile_exists = Profile.objects.filter(user=user).exists()
        assert not profile_exists  # noqa: S101

        # Save the user, which should trigger the save_user_profile signal
        user.save()

        # Check that a profile was created
        profile_exists = Profile.objects.filter(user=user).exists()
        assert profile_exists  # noqa: S101
