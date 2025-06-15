# from django.contrib import messages
# from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

# from .forms import CategoryForm
from .models import Category

# Create your views here.
# @login_required
# @permission_required("categories.add_category", raise_exception=True)
# def new_category(request):
#     """
#     View for creating a new category.
#     Only users with the 'add_category' permission can access this view.
#     """
#     if request.method == "POST":
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             category = form.save()
#             messages.success(
#                 request,
#                 f'Category "{category.name}" created successfully.',
#             )
#             return redirect("category_list")  # Redirect to category list view
#     else:
#         form = CategoryForm()
#
#     return render(request, "categories/new_category.html", {"form": form})
#
#
# @login_required
# @permission_required("categories.change_category", raise_exception=True)
# def edit_category(request, category_slug):
#     """
#     View for editing an existing category.
#     Only users with the 'change_category' permission can access this view.
#     """
#     category = get_object_or_404(Category, slug=category_slug)
#
#     if request.method == "POST":
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             category = form.save()
#             messages.success(
#                 request,
#                 f'Category "{category.name}" updated successfully.',
#             )
#             return redirect("category_list")  # Redirect to category list view
#     else:
#         form = CategoryForm(instance=category)
#
#     return render(
#         request,
#         "categories/edit_category.html",
#         {"form": form, "category": category},
#     )


def category_list(request):
    """
    View for displaying all categories with their topic counts.
    This view is accessible to all users.
    """
    # Get all categories and annotate with topic count
    categories = (Category.objects.annotate(topic_count=Count("topics")).order_by( "-name" ))

    # Set up pagination
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page = request.GET.get("page")

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        categories = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        categories = paginator.page(paginator.num_pages)

    return render(request, "categories/category_list.html", {"categories": categories})


def topics_by_category(request, category_slug):
    """
    View for displaying all topics in a specific category.
    This view shows sticky topics at the top, followed by regular topics with pagination.
    """
    # Get the category by slug
    category = get_object_or_404(Category, slug=category_slug)

    # Get sticky topics in this category, ordered by creation date
    sticky_topics = category.topics.filter(is_sticky=True).order_by("-created_at")

    # Get regular (non-sticky) topics in this category for pagination
    regular_topics_list = category.topics.filter(is_sticky=False).order_by(
        "-created_at",
    )

    # Set up pagination
    topics_per_page = 5  # Number of regular topics per page
    paginator = Paginator(regular_topics_list, topics_per_page)
    page_number = request.GET.get("page")

    try:
        regular_topics_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        regular_topics_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        regular_topics_page = paginator.page(paginator.num_pages)

    # Generate the elided page range for the regular topics
    elided_page_range = paginator.get_elided_page_range(
        number=regular_topics_page.number,
        on_each_side=2,
        on_ends=1,
    )

    context = {
        "category": category,
        "sticky_topics": sticky_topics,  # Pass sticky topics
        "regular_topics_page": regular_topics_page,  # Pass paginated regular topics
        "elided_page_range": elided_page_range,
        "PAGINATOR_ELLIPSIS": paginator.ELLIPSIS,
    }

    return render(request, "categories/topics_by_category.html", context)
