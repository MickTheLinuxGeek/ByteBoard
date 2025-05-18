# forum/views.py

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Topic, Post
# We'll need forms later: from .forms import NewTopicForm, NewPostForm
# We'll need login decorators later:
from django.contrib.auth.decorators import login_required
# We might need User model later: from django.contrib.auth.models import User

# View to display the list of all topics
def forum_index(request):
    # Query the database to get all Topic objects
    # Order them by the creation date, newest first (-created_at)
    topics = Topic.objects.order_by('-created_at').all()

    # Prepare the context dictionary to pass data to the template
    context = {
        'topics': topics,
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

# View for creating a new topic (placeholder for now)
@login_required # We'll uncomment this later to require login
def new_topic(request):
    # This view will handle both displaying the form (GET)
    # and processing the submitted form data (POST)
    # We will add form logic here in a later step.
    if request.method == 'POST':
        # Process form data (to be implemented)
        # For now, just redirect back to the index after attempting a post
        return redirect('forum:forum_index') # Redirect using the URL name
    else:
        # Display a blank form (to be implemented using Django Forms)
        # For now, just render a simple placeholder template or message
        # Let's assume we'll have a template 'forum/new_topic.html'
        return render(request, 'forum/new_topic.html') # We'll create this template

# View for creating a new post in a topic (placeholder for now)
@login_required # We'll uncomment this later
def new_post(request, topic_id):
    # Get the topic this post will belong to
    topic = get_object_or_404(Topic, pk=topic_id)

    # This view will also handle GET (show form) and POST (process form)
    # We will add form logic here later.
    if request.method == 'POST':
        # Process form data (to be implemented)
        # For now, redirect back to the topic detail page after attempting a post
        return redirect('forum:topic_detail', topic_id=topic.id) # Need to pass topic_id for the URL
    else:
        # Display a blank form (to be implemented using Django Forms)
        # We pass the topic to the template so the form knows where to post
        context = {'topic': topic}
        # Let's assume we'll have a template 'forum/new_post.html'
        return render(request, 'forum/new_post.html', context) # We'll create this template