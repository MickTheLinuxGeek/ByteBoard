# forum/forms.py

from typing import ClassVar

from django import forms

from .models import Profile


# Form for creating a new Topic AND its first Post
class NewTopicForm(forms.Form):
    subject = forms.CharField(
        max_length=255,
        required=True,
        label="Subject",  # Label displayed in the form
        widget=forms.TextInput(attrs={"placeholder": "Enter the topic subject"}),  # Customize input appearance
    )
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "Write the first post for this topic"},
        ),  # Use a textarea for longer messages
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


# Form for creating and editing user profiles
class ProfileForm(forms.ModelForm):
    """
    Form for creating and editing user profiles.iles.

    Uses ModelForm to automatically create form fields from the Profile model.
    """

    class Meta:
        model = Profile
        # Exclude user field as it's set automatically
        # Also exclude last_seen as it's updated automatically
        exclude: ClassVar[list] = ["user", "last_seen"]

        # Custom widgets for better user experience
        widgets: ClassVar[dict] = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about yourself"}),
            "signature": forms.Textarea(attrs={"rows": 3, "placeholder": "Your forum signature"}),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "avatar": forms.TextInput(attrs={"placeholder": "URL to your avatar image"}),
            "location": forms.TextInput(attrs={"placeholder": "Your location"}),
            "website": forms.URLInput(attrs={"placeholder": "https://example.com"}),
            "twitter": forms.TextInput(attrs={"placeholder": "Your Twitter username"}),
            "github": forms.TextInput(attrs={"placeholder": "Your GitHub username"}),
            "linkedin": forms.URLInput(attrs={"placeholder": "Your LinkedIn profile URL"}),
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
