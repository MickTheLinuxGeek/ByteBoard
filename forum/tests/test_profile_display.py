from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Profile

HTTP_SUCCESS = 200
HTTP_REDIRECT = 302


class TestProfileDisplay(TestCase):
    """Tests for verifying proper display of profile information."""

    def setUp(self):
        """Set up test data."""
        # Create a test user with a complete profile
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

        # Create a user with minimal profile information
        self.minimal_user = User.objects.create_user(
            username="minimaluser",
            email="minimal@example.com",
            password="minimalpassword",  # noqa: S106
        )
        self.minimal_profile = Profile.objects.get(user=self.minimal_user)
        self.minimal_profile.profile_visibility = "public"
        self.minimal_profile.save()

        # Create a user with private profile
        self.private_user = User.objects.create_user(
            username="privateuser",
            email="private@example.com",
            password="privatepassword",  # noqa: S106
        )
        self.private_profile = Profile.objects.get(user=self.private_user)
        self.private_profile.bio = "This is a private biography"
        self.private_profile.profile_visibility = "hidden"
        self.private_profile.save()

        # Set up the test client
        self.client = Client()

    def test_profile_display_complete(self):
        """Test that a complete profile displays all information correctly."""
        # Access the profile page
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that all profile information is displayed
        self.assertContains(response, "testuser")
        self.assertContains(response, "This is a test biography")
        self.assertContains(response, "Test City")
        self.assertContains(response, "https://example.com")
        self.assertContains(response, "Test User")
        self.assertContains(response, "Test Signature")
        self.assertContains(response, "testuser")  # Twitter
        self.assertContains(response, "UTC")  # Timezone

    def test_profile_display_minimal(self):
        """Test that a minimal profile displays only basic information."""
        # Access the profile page
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "minimaluser"}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that basic information is displayed
        self.assertContains(response, "minimaluser")

        # Check that optional fields are not displayed
        self.assertNotContains(response, "About Me")
        self.assertNotContains(response, "Signature")

    def test_profile_display_owner_view(self):
        """Test that the profile owner sees all information including private settings."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Access own profile page
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that private information is displayed to the owner
        self.assertContains(response, "Profile Visibility")
        self.assertContains(response, "Notification Preferences")
        self.assertContains(response, "Edit Profile")

    def test_profile_display_private(self):
        """Test that a private profile redirects non-owners."""
        # Access the private profile page without logging in
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "privateuser"}),
        )

        # Check that the user is redirected (profile_visibility_required decorator)
        assert response.status_code == HTTP_REDIRECT  # noqa: S101

        # Log in as the profile owner
        self.client.login(username="privateuser", password="privatepassword")  # noqa: S106

        # Access the profile page as the owner
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "privateuser"}),
        )

        # Check that the page loads successfully for the owner
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that private information is displayed to the owner
        self.assertContains(response, "This is a private biography")

    def test_profile_display_different_visibility_levels(self):
        """Test that different visibility levels show appropriate information."""
        # Set profile to members-only visibility
        self.profile.profile_visibility = "members"
        self.profile.save()

        # Access profile without logging in
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that non-authenticated users are redirected
        assert response.status_code == HTTP_REDIRECT  # noqa: S101

        # Log in as a different user
        self.client.login(username="minimaluser", password="minimalpassword")  # noqa: S106

        # Access the profile again
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that more information is displayed to logged-in users
        self.assertContains(response, "This is a test biography")
