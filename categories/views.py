from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from .models import Category
from .forms import CategoryForm

# Create your views here.
@login_required
@permission_required('categories.add_category', raise_exception=True)
def new_category(request):
    """
    View for creating a new category.
    Only users with the 'add_category' permission can access this view.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('category_list')  # Redirect to category list view
    else:
        form = CategoryForm()

    return render(request, 'categories/new_category.html', {'form': form})

@login_required
@permission_required('categories.change_category', raise_exception=True)
def edit_category(request, category_slug):
    """
    View for editing an existing category.
    Only users with the 'change_category' permission can access this view.
    """
    category = get_object_or_404(Category, slug=category_slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('category_list')  # Redirect to category list view
    else:
        form = CategoryForm(instance=category)

    return render(request, 'categories/edit_category.html', {'form': form, 'category': category})
