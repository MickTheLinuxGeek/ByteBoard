import io
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.request import MultiValueDict
from django.test import TestCase
from PIL import Image

from forum.forms import ProfileForm
from forum.models import Profile

# import os
# from django.core.exceptions import ValidationError
# mport pytest


class TestProfileAvatar(TestCase):
    """Tests for the Profile avatar upload and validation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="avatartest",
            email="avatar@example.com",
            password="avatarpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)

        # Create a valid test image
        self.valid_image = self._create_test_image(200, 200)

        # Create an invalid test image (too small)
        self.small_image = self._create_test_image(50, 50)

        # Create a large test image (for testing file size)
        self.large_image = self._create_test_image(1000, 1000, quality=100)

    @staticmethod
    def _create_test_image(width, height, image_format="JPEG", quality=75):
        """Helper method to create a test image file."""
        # Create a new image with the given dimensions
        image = Image.new("RGB", (width, height), color="red")

        # Save the image to a BytesIO object
        image_io = io.BytesIO()
        image.save(image_io, format=image_format, quality=quality)
        image_io.seek(0)

        # Create a SimpleUploadedFile from the BytesIO object
        return SimpleUploadedFile(
            f"test_image_{width}x{height}.jpg",
            image_io.getvalue(),
            content_type=f"image/{image_format.lower()}",
        )

    def test_valid_avatar_upload(self):
        """Test that a valid avatar can be uploaded."""
        # We need to provide all required fields for the form to be valid
        form_data = {
            "timezone": "UTC",
            "profile_visibility": "public",
            "notify_on_reply": True,
            "receive_newsletter": True,
        }
        form_files = MultiValueDict({"avatar": [self.valid_image]})
        form = ProfileForm(data=form_data, files=form_files, instance=self.profile)

        if not form.is_valid():
            print(f"Form errors: {form.errors}")

        assert form.is_valid()  # noqa: S101

    def test_small_avatar_rejected(self):
        """Test that an avatar that's too small is rejected."""
        form_data = {
            "timezone": "UTC",
            "profile_visibility": "public",
            "notify_on_reply": True,
            "receive_newsletter": True,
        }
        form_files = MultiValueDict({"avatar": [self.small_image]})
        form = ProfileForm(data=form_data, files=form_files, instance=self.profile)

        assert not form.is_valid()  # noqa: S101
        assert "avatar" in form.errors  # noqa: S101
        assert ProfileForm.ERROR_DIMENSIONS in form.errors["avatar"][0]  # noqa: S101

    def test_large_avatar_rejected(self):
        """Test that an avatar that's too large (file size) is rejected."""
        # Mock the file size to be larger than the maximum allowed
        with patch.object(
            self.large_image,
            "size",
            ProfileForm.MAX_FILE_SIZE_BYTES + 1,
        ):
            form_data = {
                "timezone": "UTC",
                "profile_visibility": "public",
                "notify_on_reply": True,
                "receive_newsletter": True,
            }
            form_files = MultiValueDict({"avatar": [self.large_image]})
            form = ProfileForm(data=form_data, files=form_files, instance=self.profile)

            assert not form.is_valid()  # noqa: S101
            assert "avatar" in form.errors  # noqa: S101
            assert ProfileForm.ERROR_FILE_SIZE in form.errors["avatar"][0]  # noqa: S101

    def test_invalid_file_type_rejected(self):
        """Test that an avatar with an invalid file type is rejected."""
        # Create a text file instead of an image
        invalid_file = SimpleUploadedFile(
            "test_file.txt",
            b"This is not an image",
            content_type="text/plain",
        )

        form_data = {
            "timezone": "UTC",
            "profile_visibility": "public",
            "notify_on_reply": True,
            "receive_newsletter": True,
        }
        form_files = MultiValueDict({"avatar": [invalid_file]})
        form = ProfileForm(data=form_data, files=form_files, instance=self.profile)

        assert not form.is_valid()  # noqa: S101
        assert "avatar" in form.errors  # noqa: S101
        # Django's built-in validation catches this before our custom validation
        # so we get a different error message
        assert "Upload a valid image" in form.errors["avatar"][0]  # noqa: S101
