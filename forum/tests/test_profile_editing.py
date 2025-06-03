from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Profile

HTTP_SUCCESS = 200
HTTP_REDIRECT = 302


class TestProfileEditing(TestCase):
    """Integration tests for the profile editing workflow."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)

        # Create a second user for testing permissions
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpassword",  # noqa: S106
        )

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",  # noqa: S106
            is_staff=True,
        )

        # Set up the test client
        self.client = Client()

    def test_profile_edit_page_access(self):
        """Test that a user can access their own profile edit page."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Access the profile edit page
        response = self.client.get(reverse("forum:edit_profile"))

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")

        # Check that the form is pre-populated with the user's profile data
        self.assertContains(response, 'name="timezone"')
        self.assertContains(response, 'name="profile_visibility"')

    def test_profile_edit_unauthorized_access(self):
        """Test that a user cannot edit another user's profile."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Try to access another user's profile edit page
        response = self.client.get(
            reverse("forum:edit_other_profile", kwargs={"username": "otheruser"}),
        )

        # Check that the user is redirected with an error message
        assert response.status_code == HTTP_REDIRECT  # Redirect status code  # noqa: S101

    def test_admin_can_edit_other_profiles(self):
        """Test that an admin can edit other users' profiles."""
        # Log in as the admin user
        self.client.login(username="adminuser", password="adminpassword")  # noqa: S106

        # Try to access another user's profile edit page
        response = self.client.get(
            reverse("forum:edit_other_profile", kwargs={"username": "testuser"}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")

    def test_profile_edit_submission(self):
        """Test that a user can successfully edit their profile."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Prepare the form data
        form_data = {
            "timezone": "America/New_York",
            "profile_visibility": "members",
            "bio": "This is my updated bio",
            "location": "New York",
            "notify_on_reply": False,
            "receive_newsletter": True,
            "signature": "This is my signature",
            "user_title": "Test User",
            "twitter": "testuser",
            "github": "testuser",
            "linkedin": "https://linkedin.com/in/testuser",
        }

        # Submit the form
        response = self.client.post(
            reverse("forum:edit_profile"),
            form_data,
            follow=True,
        )

        # Check that the user is redirected to their profile page
        self.assertRedirects(
            response,
            reverse("forum:user_profile", kwargs={"username": "testuser"}),
        )

        # Check that the profile was updated in the database
        self.profile.refresh_from_db()
        assert self.profile.timezone == "America/New_York"  # noqa: S101
        assert self.profile.profile_visibility == "members"  # noqa: S101
        assert self.profile.bio == "This is my updated bio"  # noqa: S101
        assert self.profile.location == "New York"  # noqa: S101
        assert not self.profile.notify_on_reply  # noqa: S101
        assert self.profile.receive_newsletter  # noqa: S101
        assert self.profile.signature == "This is my signature"  # noqa: S101
        assert self.profile.user_title == "Test User"  # noqa: S101
        assert self.profile.twitter == "testuser"  # noqa: S101
        assert self.profile.github == "testuser"  # noqa: S101
        assert self.profile.linkedin == "https://linkedin.com/in/testuser"  # noqa: S101

    def test_profile_edit_invalid_data(self):
        """Test that invalid form data is rejected."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Prepare invalid form data (invalid timezone)
        form_data = {
            "timezone": "Invalid_Timezone",
            "profile_visibility": "public",
            "notify_on_reply": True,
            "receive_newsletter": True,
        }

        # Submit the form
        response = self.client.post(reverse("forum:edit_profile"), form_data)

        # Check that the form is displayed again with errors
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")
        self.assertFormError(
            response.context["form"],
            "timezone",
            "Select a valid choice. Invalid_Timezone is not one of the available choices.",
        )
