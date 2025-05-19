# forum/views.py

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Topic, Post
# We'll need forms later:
from .forms import NewTopicForm, NewPostForm
# We'll need login decorators later:
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden  # For permission errors
from django.utils import timezone  # Import timezone
from django.contrib.auth.forms import UserCreationForm  # Import Django's registration form
from django.contrib.auth import login  # Import the login function
# Import pagination classes
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# We might need User model later: from django.contrib.auth.models import User

# View to display the list of all topics
def forum_index(request):
    # Query the database to get all Topic objects
    all_topics_list = Topic.objects.order_by('-created_at').all()

    # Set the number of topics per page
    topics_per_page = 10  # You can adjust this number

    # Create a Paginator object
    paginator = Paginator(all_topics_list, topics_per_page)

    # Get the current page number from the GET request (e.g., ?page=2)
    page_number = request.GET.get('page')

    try:
        # Get the Page object for the requested page number
        topics_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        topics_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        topics_page = paginator.page(paginator.num_pages)

    # Prepare the context dictionary to pass data to the template
    # We pass the 'Page' object, not the full list of topics
    context = {
        'topics_page': topics_page,
    }

    # Render the template 'forum/forum_index.html' with the context data
    return render(request, 'forum/forum_index.html', context)


# View to display a single topic and its posts
def topic_detail(request, topic_id):
    # Get the specific Topic object by its primary key (topic_id)
    # If the topic doesn't exist, it automatically raises a 404 Not Found error
    topic = get_object_or_404(Topic, pk=topic_id)

    # Get all Post objects related to this specific topic
    # Order them by creation date, oldest first (default or use order_by('created_at'))
    posts = topic.posts.order_by('created_at').all()

    # Prepare the context
    context = {
        'topic': topic,
        'posts': posts,
    }

    # Render the template 'forum/topic_detail.html'
    return render(request, 'forum/topic_detail.html', context)


@login_required
def new_topic(request):
    if request.method == 'POST':
        # Instantiate the form with submitted data
        form = NewTopicForm(request.POST)
        if form.is_valid():  # Check if the form data is valid
            # Get the cleaned data from the form
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            user = request.user  # Get the currently logged-in user

            # Create the Topic instance
            topic = Topic.objects.create(
                subject=subject,
                created_by=user
            )

            # Create the initial Post instance for this topic
            Post.objects.create(
                message=message,
                topic=topic,
                created_by=user
            )

            # Redirect to the newly created topic's detail page
            return redirect('forum:topic_detail', topic_id=topic.pk)
        # If form is not valid, execution continues to the render statement below,
        # and the 'form' instance now contains errors.
    else:
        # GET request: Create a blank instance of the form
        form = NewTopicForm()

    # Render the template with the form (either blank or with errors)
    context = {'form': form}
    return render(request, 'forum/new_topic.html', context)


@login_required
def new_post(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            user = request.user

            # Create the Post instance, linking it to the topic and user
            Post.objects.create(
                message=message,
                topic=topic,
                created_by=user
            )
            # Optionally, update the topic's last_updated field here if you add one

            # Redirect back to the topic detail page
            return redirect('forum:topic_detail', topic_id=topic.pk)
        # If form is invalid, render the page again with the form containing errors
    else:
        # GET request: Create a blank instance of the form
        form = NewPostForm()

    # Render the template with the topic and the form
    context = {
        'topic': topic,
        'form': form,
    }
    return render(request, 'forum/new_post.html', context)


# View for user registration/signup
def signup(request):
    if request.method == 'POST':
        # Instantiate the form with the submitted data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Form is valid, save the new user
            user = form.save()  # This creates the user instance with a hashed password
            # Log the user in automatically after successful registration
            login(request, user)
            # Redirect to the forum index page
            return redirect('forum:forum_index')
        # If form is invalid, execution continues to the render statement below,
        # and the 'form' instance now contains errors (e.g., username taken, passwords don't match)
    else:
        # GET request: Create a blank instance of the form
        form = UserCreationForm()

    # Render the template with the form (either blank or with errors)
    context = {'form': form}
    # We'll create this template in the project's templates/registration directory
    return render(request, 'registration/signup.html', context)


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

    if request.method == 'POST':
        # Pass instance=post to pre-populate and update the existing post if using ModelForm
        # If using forms.Form, we handle it slightly differently
        form = NewPostForm(request.POST)  # Re-use NewPostForm
        if form.is_valid():
            post.message = form.cleaned_data['message']
            post.updated_at = timezone.now()  # Set the updated_at timestamp
            post.save()
            # Redirect to the topic detail page where the post is located
            return redirect('forum:topic_detail', topic_id=post.topic.id)
    else:
        # GET request: Populate the form with the existing post's message
        form = NewPostForm(initial={'message': post.message})

    context = {
        'form': form,
        'post': post,  # Pass the post object for context in the template
        'topic': post.topic  # Pass topic for breadcrumbs or cancel link
    }
    return render(request, 'forum/edit_post.html', context)
