from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Profile

HTTP_SUCCESS = 200


class TestResponsiveDesign(TestCase):
    """Tests for verifying responsive design of profile pages."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)

        # Update profile with test data
        self.profile.bio = "This is a test biography"
        self.profile.location = "Test City"
        self.profile.website = "https://example.com"
        self.profile.user_title = "Test User"
        self.profile.signature = "Test Signature"
        self.profile.twitter = "testuser"
        self.profile.github = "testuser"
        self.profile.linkedin = "https://linkedin.com/in/testuser"
        self.profile.timezone = "UTC"
        self.profile.profile_visibility = "public"
        self.profile.save()

        # Set up the test client
        self.client = Client()

        # Define different viewport sizes for testing
        self.mobile_viewport = {
            "HTTP_USER_AGENT": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        }
        self.tablet_viewport = {
            "HTTP_USER_AGENT": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
        }
        self.desktop_viewport = {
            "HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }

    def test_profile_view_responsive_elements(self):
        """Test that the profile view page contains responsive design elements."""
        # Access the profile page
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check for responsive meta tag
        self.assertContains(response, '<meta name="viewport"')

        # Check for responsive CSS classes or elements
        self.assertContains(response, 'class="profile-header"')
        self.assertContains(response, 'class="profile-info"')
        self.assertContains(response, 'class="user-activity"')

    def test_profile_edit_responsive_elements(self):
        """Test that the profile edit page contains responsive design elements."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Access the profile edit page
        response = self.client.get(reverse("forum:edit_profile"))

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check for responsive meta tag
        self.assertContains(response, '<meta name="viewport"')

        # Check for responsive form elements
        self.assertContains(response, 'class="form-group"')
        self.assertContains(response, 'class="form-section"')
        self.assertContains(response, 'class="form-actions"')

    def test_profile_view_different_viewports(self):
        """Test that the profile view page loads correctly on different viewports."""
        # Test mobile viewport
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
            **self.mobile_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Test tablet viewport
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
            **self.tablet_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Test desktop viewport
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
            **self.desktop_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

    def test_profile_edit_different_viewports(self):
        """Test that the profile edit page loads correctly on different viewports."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Test mobile viewport
        response = self.client.get(
            reverse("forum:edit_profile"),
            **self.mobile_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Test tablet viewport
        response = self.client.get(
            reverse("forum:edit_profile"),
            **self.tablet_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Test desktop viewport
        response = self.client.get(
            reverse("forum:edit_profile"),
            **self.desktop_viewport,
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

    def test_avatar_responsive_sizing(self):
        """Test that avatar images use responsive sizing attributes."""
        # Access the profile page
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check for responsive image attributes
        self.assertContains(response, 'class="avatar-img"')

        # Check that the avatar container has a responsive class
        self.assertContains(response, 'class="profile-avatar"')
