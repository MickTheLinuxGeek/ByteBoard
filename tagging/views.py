from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from forum.models import Post

from .models import Tag

# Create your views here.

def tag_suggestions(request):
    """
    View to provide tag suggestions for autocomplete.

    Accepts a 'query' parameter and returns matching tags as JSON.
    Tags are matched if they start with or contain the query string.
    """
    query = request.GET.get("query", "").strip().lower()

    if not query:
        return JsonResponse({"tags": []})

    # Find tags that start with the query (higher priority) or contain the query
    # Order by name to provide consistent results
    tags = Tag.objects.filter(
        Q(name__startswith=query) | Q(name__contains=query),
    ).order_by("name").distinct().values_list("name", flat=True)[:10]  # Limit to 10 suggestions

    return JsonResponse({"tags": list(tags)})

def posts_by_tag(request, tag_slug):
    """
    View to display all posts with a specific tag.

    Includes post snippets, author information, and links to original topics.
    Implements pagination for posts.
    Displays the tag name in the page title.
    """
    # Get the tag or return 404 if not found
    tag = get_object_or_404(Tag, slug=tag_slug)

    # Get all posts with this tag, ordered by creation date (newest first)
    posts = Post.objects.filter(tags=tag).order_by("-created_at")

    # Set up pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page = request.GET.get("page")

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts_page = paginator.page(paginator.num_pages)

    return render(request, "tagging/posts_by_tag.html", {
        "tag": tag,
        "posts": posts_page,
    })

def tag_list(request):
    """
    View to display all available tags.

    Includes tag name and post count.
    Implements pagination if there are many tags.
    Also includes a tag cloud where font size is proportional to post count.
    """
    # Get all tags and annotate them with post count
    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')

    # Set up pagination
    paginator = Paginator(tags, 20)  # Show 20 tags per page
    page = request.GET.get("page")

    try:
        tags_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        tags_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        tags_page = paginator.page(paginator.num_pages)

    # Prepare tags for the tag cloud
    # Get the top 30 tags by post count for the cloud
    cloud_tags = list(tags[:30])

    # Calculate font sizes for the tag cloud
    if cloud_tags:
        # Find the minimum and maximum post counts
        min_count = min(tag.post_count for tag in cloud_tags)
        max_count = max(tag.post_count for tag in cloud_tags)

        # Calculate font size for each tag (between 0.8em and 2.5em)
        min_font_size = 0.8
        max_font_size = 2.5

        for tag in cloud_tags:
            if max_count == min_count:  # Avoid division by zero
                tag.font_size = (min_font_size + max_font_size) / 2
            else:
                # Calculate font size based on post count
                tag.font_size = min_font_size + (
                    (tag.post_count - min_count) / (max_count - min_count)
                ) * (max_font_size - min_font_size)

    return render(request, "tagging/tag_list.html", {
        "tags": tags_page,
        "cloud_tags": cloud_tags,
    })
