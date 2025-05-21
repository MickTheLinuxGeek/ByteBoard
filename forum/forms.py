# forum/forms.py

from django import forms


# Note: We are NOT importing models here for the basic forms.Form approach
# from .models import Topic, Post # (We would need this for ModelForms)

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
