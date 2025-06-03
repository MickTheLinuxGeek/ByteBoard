from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Profile

HTTP_SUCCESS = 200
HTTP_REDIRECT = 302


class TestProfilePermissions(TestCase):
    """Integration tests for profile permissions and visibility settings."""

    def setUp(self):
        """Set up test data."""
        # Create users with different profile visibility settings
        self.public_user = User.objects.create_user(
            username="publicuser",
            email="public@example.com",
            password="publicpassword",  # noqa: S106
        )
        self.public_profile = Profile.objects.get(user=self.public_user)
        self.public_profile.profile_visibility = "public"
        self.public_profile.bio = "This is a public profile"
        self.public_profile.save()

        self.members_user = User.objects.create_user(
            username="membersuser",
            email="members@example.com",
            password="memberspassword",  # noqa: S106
        )
        self.members_profile = Profile.objects.get(user=self.members_user)
        self.members_profile.profile_visibility = "members"
        self.members_profile.bio = "This is a members-only profile"
        self.members_profile.save()

        self.hidden_user = User.objects.create_user(
            username="hiddenuser",
            email="hidden@example.com",
            password="hiddenpassword",  # noqa: S106
        )
        self.hidden_profile = Profile.objects.get(user=self.hidden_user)
        self.hidden_profile.profile_visibility = "hidden"
        self.hidden_profile.bio = "This is a hidden profile"
        self.hidden_profile.save()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",  # noqa: S106
            is_staff=True,
        )

        # Create a regular user for testing
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpassword",  # noqa: S106
        )

        # Set up the test client
        self.client = Client()

    def test_public_profile_visibility(self):
        """Test that a public profile is visible to everyone."""
        # Test anonymous user access
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "publicuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a public profile")

        # Test authenticated user access
        self.client.login(username="regularuser", password="regularpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "publicuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a public profile")

    def test_members_profile_visibility(self):
        """Test that a members-only profile is visible only to authenticated users."""
        # Test anonymous user access (should be redirected)
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "membersuser"}),
        )
        assert (  # noqa: S101
            response.status_code == HTTP_REDIRECT
        )  # Redirect status code

        # Test authenticated user access
        self.client.login(username="regularuser", password="regularpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "membersuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a members-only profile")

    def test_hidden_profile_visibility(self):
        """Test that a hidden profile is visible only to the owner and admins."""
        # Test anonymous user access (should be redirected)
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert (  # noqa: S101
            response.status_code == HTTP_REDIRECT
        )  # Redirect status code

        # Test authenticated but unauthorized user access (should be redirected)
        self.client.login(username="regularuser", password="regularpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert (  # noqa: S101
            response.status_code == HTTP_REDIRECT
        )  # Redirect status code

        # Test profile owner access
        self.client.login(username="hiddenuser", password="hiddenpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a hidden profile")

        # Test admin access
        self.client.login(username="adminuser", password="adminpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a hidden profile")

    def test_profile_owner_access(self):
        """Test that profile owners can always access their own profiles."""
        # Test hidden profile owner access
        self.client.login(username="hiddenuser", password="hiddenpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a hidden profile")

        # Test members-only profile owner access
        self.client.login(username="membersuser", password="memberspassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "membersuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a members-only profile")

    def test_admin_access(self):
        """Test that admins can access all profiles regardless of visibility settings."""
        self.client.login(username="adminuser", password="adminpassword")  # noqa: S106

        # Test access to public profile
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "publicuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a public profile")

        # Test access to members-only profile
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "membersuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a members-only profile")

        # Test access to hidden profile
        response = self.client.get(
            reverse("forum:user_profile", kwargs={"username": "hiddenuser"}),
        )
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertContains(response, "This is a hidden profile")
