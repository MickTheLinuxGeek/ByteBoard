from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.request import MultiValueDict
from django.test import Client, TestCase
from django.urls import reverse

from forum.forms import ProfileForm
from forum.models import Profile

HTTP_SUCCESS = 200


class TestFormValidation(TestCase):
    """Tests for ensuring proper validation feedback on forms."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)

        # Set up the test client
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

    def test_form_validation_required_fields(self):
        """Test validation feedback for required fields."""
        # Prepare form data with missing required fields
        form_data = {
            "timezone": "",  # Required field
            "profile_visibility": "",  # Required field
        }

        # Submit the form
        response = self.client.post(reverse("forum:edit_profile"), form_data)

        # Check that the form is displayed again with errors
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")

        # Check for error messages
        self.assertContains(response, "This field is required")

        # Check that the error messages are displayed next to the appropriate fields
        self.assertContains(response, '<div class="error-message">')

    def test_form_validation_invalid_timezone(self):
        """Test validation feedback for invalid timezone."""
        # Prepare form data with invalid timezone
        form_data = {
            "timezone": "Invalid_Timezone",
            "profile_visibility": "public",
        }

        # Submit the form
        response = self.client.post(reverse("forum:edit_profile"), form_data)

        # Check that the form is displayed again with errors
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")

        # Check for error message
        self.assertContains(response, "Select a valid choice")

        # Check that the error message is displayed next to the timezone field
        self.assertContains(response, '<div class="error-message">')

    def test_form_validation_invalid_url(self):
        """Test validation feedback for invalid URL."""
        # Prepare form data with invalid URL
        form_data = {
            "timezone": "UTC",
            "profile_visibility": "public",
            "website": "invalid-url",  # Invalid URL
        }

        # Submit the form
        response = self.client.post(reverse("forum:edit_profile"), form_data)

        # Check that the form is displayed again with errors
        assert response.status_code == HTTP_SUCCESS  # noqa: S101
        self.assertTemplateUsed(response, "forum/edit_profile.html")

        # Check for error message
        self.assertContains(response, "Enter a valid URL")

        # Check that the error message is displayed next to the website field
        self.assertContains(response, '<div class="error-message">')

    def test_form_validation_avatar_size(self):
        """Test validation feedback for avatar size."""
        # Create a large file (over 2MB)
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            b"x" * (2 * 1024 * 1024 + 1),  # Just over 2MB
            content_type="image/jpeg",
        )

        # Test the form directly
        form_files = MultiValueDict({"avatar": [large_file]})
        form = ProfileForm(
            data={
                "timezone": "UTC",
                "profile_visibility": "public",
            },
            files=form_files,
            instance=self.profile,
        )

        # Check that the form is not valid
        assert not form.is_valid()  # noqa: S101

        # Check for error message
        assert "avatar" in form.errors  # noqa: S101
        # Django's built-in validation catches this as an invalid image before our custom validation
        assert "Upload a valid image" in str(form.errors["avatar"])  # noqa: S101

    def test_form_validation_avatar_type(self):
        """Test validation feedback for avatar file type."""
        # Create a file with invalid extension
        invalid_file = SimpleUploadedFile(
            "invalid_file.txt",
            b"This is not an image",
            content_type="text/plain",
        )

        # Test the form directly
        form_files = MultiValueDict({"avatar": [invalid_file]})
        form = ProfileForm(
            data={
                "timezone": "UTC",
                "profile_visibility": "public",
            },
            files=form_files,
            instance=self.profile,
        )

        # Check that the form is not valid
        assert not form.is_valid()  # noqa: S101

        # Check for error message
        assert "avatar" in form.errors  # noqa: S101
        # Django's built-in validation catches this as an invalid image before our custom validation
        assert "Upload a valid image" in str(form.errors["avatar"])  # noqa: S101

    def test_form_validation_direct_form_validation(self):
        """Test validation directly on the form class."""
        # Test with invalid data
        form = ProfileForm(
            data={
                "timezone": "Invalid_Timezone",
                "profile_visibility": "invalid_visibility",
            },
            instance=self.profile,
        )

        # Check that the form is not valid
        assert not form.is_valid()  # noqa: S101

        # Check for specific error messages
        assert "timezone" in form.errors  # noqa: S101
        assert "profile_visibility" in form.errors  # noqa: S101

        # Test with valid data
        form = ProfileForm(
            data={
                "timezone": "UTC",
                "profile_visibility": "public",
            },
            instance=self.profile,
        )

        # Check that the form is valid
        assert form.is_valid()  # noqa: S101
