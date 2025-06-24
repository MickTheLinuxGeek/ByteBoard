# forum/forms.py

import pathlib
from typing import ClassVar, cast

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from PIL import Image

from categories.models import Category
from tagging.models import Tag
from .models import Profile


# Custom widget for tag input
class TagInputWidget(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'tag-input', 'placeholder': 'Enter tags separated by commas'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

# Form for creating a new Topic AND its first Post
class NewTopicForm(forms.Form):
    subject = forms.CharField(
        max_length=255,
        required=True,
        label="Subject",  # Label displayed in the form
        widget=forms.TextInput(
            attrs={"placeholder": "Enter the topic subject"},
        ),  # Customize input appearance
    )
    category = forms.ModelChoiceField(
        queryset=cast(QuerySet, Category.objects.all()),
        required=True,
        label="Category",
        empty_label="Select a category",
    )
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "Write the first post for this topic"},
        ),  # Use a textarea for longer messages
    )
    tags = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas (e.g., python, django, web-development)",
        widget=TagInputWidget(),
    )


# Form for creating a new Post (reply)
class NewPostForm(forms.Form):
    message = forms.CharField(
        required=True,
        label="Your Reply",
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "Write your reply"},
        ),
    )
    tags = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas (e.g., python, django, web-development)",
        widget=TagInputWidget(),
    )


# Form for creating and editing user profiles
class ProfileForm(forms.ModelForm):
    # File validation constants
    MAX_FILE_SIZE_MB = 2
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    VALID_EXTENSIONS: ClassVar[list] = [".jpg", ".jpeg", ".png", ".gif"]

    # Image dimension constants
    IMAGE_HEIGHT_MIN = 100
    IMAGE_WIDTH_MIN = 100
    IMAGE_HEIGHT_MAX = 1000  # Assuming this was defined elsewhere
    IMAGE_WIDTH_MAX = 1000  # Assuming this was defined elsewhere

    # Error messages
    ERROR_FILE_SIZE = (
        f"Image file too large. Please keep it under {MAX_FILE_SIZE_MB}MB."
    )
    ERROR_FILE_TYPE = (
        f"Unsupported file extension. Please use {', '.join(VALID_EXTENSIONS)}"
    )
    ERROR_DIMENSIONS = f"Image too small. Minimum dimensions are {IMAGE_WIDTH_MIN}x{IMAGE_HEIGHT_MIN} pixels."

    def clean_avatar(self) -> object | None:
        """
        Validates the uploaded avatar image.

        Checks:
        - File size (max 2MB)
        - File type (must be jpg, jpeg, png, or gif)
        - Image dimensions (minimum 100x100 pixels)

        Returns:
        - object | None: The validated avatar file or None if no file was uploaded
        Raises:
        ValidationError: If any validation check fails

        """
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        self._validate_file_size(avatar)
        self._validate_file_type(avatar)
        self._validate_image_dimensions(avatar)

        return avatar

    def _validate_file_size(self, avatar) -> None:
        if avatar.size > self.MAX_FILE_SIZE_BYTES:
            raise ValidationError(self.ERROR_FILE_SIZE)

    def _validate_file_type(self, avatar) -> None:
        ext = pathlib.Path(avatar.name).suffix.lower()
        if ext not in self.VALID_EXTENSIONS:
            raise ValidationError(self.ERROR_FILE_TYPE)

    def _validate_image_dimensions(self, avatar) -> None:
        def raise_dimension_error():
            raise ValidationError(self.ERROR_DIMENSIONS)

        def raise_invalid_image(exp):
            msg = f"Invalid image file: {exp!s}"
            raise ValidationError(msg) from exp

        try:
            img = Image.open(avatar)
            if img.height < self.IMAGE_HEIGHT_MIN or img.width < self.IMAGE_WIDTH_MIN:
                raise_dimension_error()
            # Note: Large images will be resized in the view after saving
        # except Exception as e:
        except ValidationError as e:
            raise_invalid_image(e)

    class Meta:
        model = Profile
        # Exclude user field as it's set automatically
        # Also exclude last_seen as it's updated automatically
        exclude: ClassVar[list] = ["user", "last_seen"]

        # Custom widgets for better user experience
        widgets: ClassVar[dict] = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us about yourself"},
            ),
            "signature": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Your forum signature"},
            ),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
            "location": forms.TextInput(attrs={"placeholder": "Your location"}),
            "website": forms.URLInput(attrs={"placeholder": "https://example.com"}),
            "twitter": forms.TextInput(attrs={"placeholder": "Your Twitter username"}),
            "github": forms.TextInput(attrs={"placeholder": "Your GitHub username"}),
            "linkedin": forms.URLInput(
                attrs={"placeholder": "Your LinkedIn profile URL"},
            ),
        }

        # Custom labels for fields
        labels: ClassVar[dict] = {
            "bio": "Biography",
            "user_title": "Forum Title",
            "notify_on_reply": "Notify me when someone replies to my posts",
            "receive_newsletter": "Receive forum newsletter",
            "profile_visibility": "Profile Visibility",
        }

        # Help text for fields
        help_texts: ClassVar[dict] = {
            "profile_visibility": "Who can see your profile information",
            "timezone": "Select your local timezone",
            "signature": "This will be displayed at the bottom of your posts",
        }
