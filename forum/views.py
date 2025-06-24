# forum/views.py

# Create your views here.

from django.contrib import messages  # Import messages framework
from django.contrib.auth import login  # Import the login function

# We'll need login decorators later:
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    UserCreationForm,  # Import Django's registration form
)

# We might need User model later:
from django.contrib.auth.models import User

# Import pagination classes
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseForbidden  # For permission errors
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone  # Import timezone
from PIL import Image, UnidentifiedImageError

from tagging.models import Tag

# We'll need forms later:
from .decorators import profile_visibility_required
from .forms import NewPostForm, NewTopicForm, ProfileForm
from .models import Post, Profile, Topic

IMAGE_HEIGHT_MAX = 500
IMAGE_WIDTH_MAX = 500


# View to display the list of all topics with sticky topics at the top
def forum_index(request):
    # Get sticky topics, ordered by creation date (or another preferred field)
    sticky_topics = Topic.objects.filter(is_sticky=True).order_by("-created_at")

    # Get regular (non-sticky) topics for pagination
    regular_topics_list = Topic.objects.filter(is_sticky=False).order_by("-created_at")

    topics_per_page = 5  # Number of regular topics per page
    paginator = Paginator(regular_topics_list, topics_per_page)
    page_number = request.GET.get("page")

    try:
        regular_topics_page = paginator.page(page_number)
    except PageNotAnInteger:
        regular_topics_page = paginator.page(1)
    except EmptyPage:
        regular_topics_page = paginator.page(paginator.num_pages)

    # Generate the elided page range for the regular topics
    elided_page_range = paginator.get_elided_page_range(
        number=regular_topics_page.number,
        on_each_side=2,
        on_ends=1,
    )

    context = {
        "sticky_topics": sticky_topics,  # Pass sticky topics
        "regular_topics_page": regular_topics_page,  # Pass paginated regular topics
        "elided_page_range": elided_page_range,
        "PAGINATOR_ELLIPSIS": paginator.ELLIPSIS,
    }
    return render(request, "forum/forum_index.html", context)


# View to display a single topic and its posts
def topic_detail(request, topic_id):
    # Get the specific Topic object by its primary key (topic_id)
    # If the topic doesn't exist, it automatically raises a 404 Not Found error
    topic = get_object_or_404(Topic, pk=topic_id)

    # Get all Post objects related to this specific topic
    # Order them by creation date, oldest first (default or use order_by('created_at'))
    posts = topic.posts.order_by("created_at").all()

    # Prepare the context
    context = {
        "topic": topic,
        "posts": posts,
    }

    # Render the template 'forum/topic_detail.html'
    return render(request, "forum/topic_detail.html", context)


@login_required
def new_topic(request):
    if request.method == "POST":
        # Instantiate the form with submitted data
        form = NewTopicForm(request.POST)
        if form.is_valid():  # Check if the form data is valid
            # Get the cleaned data from the form
            subject = form.cleaned_data["subject"]
            category = form.cleaned_data["category"]
            message = form.cleaned_data["message"]
            user = request.user  # Get the currently logged-in user

            # Create the Topic instance
            topic = Topic.objects.create(
                subject=subject,
                created_by=user,
                category=category,
            )

            # Create the initial Post instance for this topic
            post = Post.objects.create(
                message=message,
                topic=topic,
                created_by=user,
            )

            # Process tags if provided
            tags_input = form.cleaned_data.get("tags", "")
            if tags_input:
                # Split the comma-separated tags and strip whitespace
                tag_names = [tag.strip().lower() for tag in tags_input.split(",") if tag.strip()]

                # Process each tag
                for tag_name in tag_names:
                    # Get or create the tag
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    # Add the tag to the post
                    post.tags.add(tag)

            # Redirect to the newly created topic's detail page
            return redirect("forum:topic_detail", topic_id=topic.pk)
        # If form is not valid, execution continues to the render statement below,
        # and the 'form' instance now contains errors.
    else:
        # GET request: Create a blank instance of the form
        form = NewTopicForm()

    # Render the template with the form (either blank or with errors)
    context = {"form": form}
    return render(request, "forum/new_topic.html", context)


@login_required
def new_post(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data["message"]
            user = request.user

            # Create the Post instance, linking it to the topic and user
            post = Post.objects.create(
                message=message,
                topic=topic,
                created_by=user,
            )

            # Process tags if provided
            tags_input = form.cleaned_data.get("tags", "")
            if tags_input:
                # Split the comma-separated tags and strip whitespace
                tag_names = [tag.strip().lower() for tag in tags_input.split(",") if tag.strip()]

                # Process each tag
                for tag_name in tag_names:
                    # Get or create the tag
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    # Add the tag to the post
                    post.tags.add(tag)
            # Optionally, update the topic's last_updated field here if you add one

            # Redirect back to the topic detail page
            return redirect("forum:topic_detail", topic_id=topic.pk)
        # If form is invalid, render the page again with the form containing errors
    else:
        # GET request: Create a blank instance of the form
        form = NewPostForm()

    # Render the template with the topic and the form
    context = {
        "topic": topic,
        "form": form,
    }
    return render(request, "forum/new_post.html", context)


# View for user registration/signup
def signup(request):
    if request.method == "POST":
        # Instantiate the form with the submitted data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Form is valid, save the new user
            user = form.save()  # This creates the user instance with a hashed password
            # Log the user in automatically after successful registration
            login(request, user)
            # Redirect to the forum index page
            return redirect("forum:forum_index")
        # If form is invalid, execution continues to the render statement below,
        # and the 'form' instance now contains errors (e.g., username taken, passwords don't match)
    else:
        # GET request: Create a blank instance of the form
        form = UserCreationForm()

    # Render the template with the form (either blank or with errors)
    context = {"form": form}
    # We'll create this template in the project's templates/registration directory
    return render(request, "registration/signup.html", context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Check if the current user is the author of the post
    if post.created_by != request.user:
        # If not, return a forbidden response or redirect
        return HttpResponseForbidden("You are not allowed to edit this post.")
        # Alternatively, you could redirect with a message:
        # from django.contrib import messages
        # messages.error(request, "You do not have permission to edit this post.")
        # return redirect('forum:topic_detail', topic_id=post.topic.id)

    if request.method == "POST":
        # Pass instance=post to pre-populate and update the existing post if using ModelForm
        # If using forms.Form, we handle it slightly differently
        form = NewPostForm(request.POST)  # Re-use NewPostForm
        if form.is_valid():
            post.message = form.cleaned_data["message"]
            post.updated_at = timezone.now()  # Set the updated_at timestamp
            post.save()

            # Process tags if provided
            tags_input = form.cleaned_data.get("tags", "")

            # Clear existing tags
            post.tags.clear()

            if tags_input:
                # Split the comma-separated tags and strip whitespace
                tag_names = [tag.strip().lower() for tag in tags_input.split(",") if tag.strip()]

                # Process each tag
                for tag_name in tag_names:
                    # Get or create the tag
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    # Add the tag to the post
                    post.tags.add(tag)
            # Redirect to the topic detail page where the post is located
            return redirect("forum:topic_detail", topic_id=post.topic.id)
    else:
        # GET request: Populate the form with the existing post's message and tags
        # Get existing tags as a comma-separated string
        existing_tags = ", ".join([tag.name for tag in post.tags.all()])
        form = NewPostForm(initial={"message": post.message, "tags": existing_tags})

    context = {
        "form": form,
        "post": post,  # Pass the post object for context in the template
        "topic": post.topic,  # Pass topic for breadcrumbs or cancel link
    }
    return render(request, "forum/edit_post.html", context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    topic_id_for_redirect = post.topic.id  # Store topic ID before post is deleted

    # Check if the current user is the author of the post
    if post.created_by != request.user:
        # If not, return a forbidden response or redirect
        messages.error(request, "You are not allowed to delete this post.")
        return redirect("forum:topic_detail", topic_id=topic_id_for_redirect)

    if request.method == "POST":
        # User has confirmed deletion via POST request
        post_message_preview = post.message[:30]  # For the message
        post.delete()
        messages.success(request, f"Post '{post_message_preview}...' has been deleted.")
        # Redirect to the topic detail page where the post was
        return redirect("forum:topic_detail", topic_id=topic_id_for_redirect)
    # GET request: Display confirmation page
    context = {
        "post": post,
        "topic": post.topic,  # For cancel link and context
    }
    return render(request, "forum/delete_post_confirm.html", context)


@profile_visibility_required
def user_profile(request, username):
    # Get the User object for the requested username, or raise a 404 if not found
    profile_user = get_object_or_404(User, username=username)

    # Get the profile and its visibility setting
    profile = profile_user.profile
    visibility = profile.profile_visibility

    # Determine the level of profile information to display
    # 0 = Basic info only (username, join date, post count)
    # 1 = Standard info (basic + location, website, bio, signature, social links)
    # 2 = Full info (standard + birth date, notification preferences)
    info_level = 0

    # Profile owner and admins can see everything
    if (
        request.user == profile_user
        or request.user.is_staff
        or request.user.is_superuser
    ):
        info_level = 2
    # Members can see standard info for "members" and "public" profiles
    elif (
        request.user.is_authenticated and (visibility in {"members", "public"})
    ) or visibility == "public":
        info_level = 1
    # Otherwise, only basic info is shown (handled by default info_level = 0)

    # Get topics created by this user, ordered by most recent
    user_topics = Topic.objects.filter(created_by=profile_user).order_by("-created_at")

    # Get posts created by this user, ordered by most recent
    # For performance, you might want to limit this, e.g., user_posts.all()[:20]
    user_posts = Post.objects.filter(created_by=profile_user).order_by("-created_at")

    context = {
        "profile_user": profile_user,
        "user_topics": user_topics,
        "user_posts": user_posts,
        "visibility": visibility,  # Pass visibility to the template
        "info_level": info_level,  # Pass info level to the template
        "is_owner": request.user == profile_user,  # Is the viewer the profile owner?
        "is_admin": request.user.is_staff
        or request.user.is_superuser,  # Is the viewer an admin?
    }
    return render(request, "forum/user_profile.html", context)


@login_required
def edit_profile(request, username=None):
    """View for editing user profile information including avatar upload."""
    # If username is provided, get that user's profile, otherwise use the current user's profile
    if username and username != request.user.username:
        # Check if the current user is an admin
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "You don't have permission to edit this profile.")
            return redirect("forum:forum_index")

        # Get the user whose profile we're editing
        user = get_object_or_404(User, username=username)
        profile, created = Profile.objects.get_or_create(user=user)
    else:
        # Get the current user's profile or create one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save the form without committing to process the avatar
            profile = form.save(commit=False)

            # Handle avatar resizing if needed
            if "avatar" in request.FILES:
                avatar_file = request.FILES["avatar"]
                # Resize large images
                try:
                    img = Image.open(avatar_file)
                    if img.height > IMAGE_HEIGHT_MAX or img.width > IMAGE_WIDTH_MAX:
                        # Calculate new dimensions while maintaining aspect ratio
                        if img.height > img.width:
                            ratio = 500.0 / img.height
                            new_height = 500
                            new_width = int(img.width * ratio)
                        else:
                            ratio = 500.0 / img.width
                            new_width = 500
                            new_height = int(img.height * ratio)

                        # Resize the image
                        img = img.resize(
                            (new_width, new_height),
                            Image.Resampling.LANCZOS,
                        )

                        # Save the resized image back to the avatar field
                        # This requires saving to a temporary file
                        import io

                        from django.core.files.uploadedfile import InMemoryUploadedFile

                        output = io.BytesIO()
                        # Determine the format from the original file
                        avatar_format = avatar_file.name.split(".")[-1].upper()
                        if avatar_format == "JPG":
                            avatar_format = "JPEG"

                        # Save to the BytesIO object
                        img.save(output, format=avatar_format, quality=85)
                        output.seek(0)

                        # Replace the avatar file with the resized version
                        profile.avatar = InMemoryUploadedFile(
                            output,
                            "ImageField",
                            avatar_file.name,
                            f"image/{avatar_format.lower()}",
                            output.getbuffer().nbytes,
                            None,
                        )
                # except Exception as e:
                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError,
                    AttributeError,
                    IndexError,
                    TypeError,
                ) as e:
                    messages.error(request, f"Error processing image: {e!s}")

            # Save the profile
            profile.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("forum:user_profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "forum/edit_profile.html", {"form": form})
