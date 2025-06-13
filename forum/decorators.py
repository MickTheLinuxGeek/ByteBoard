# forum/decorators.py

from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import User


def profile_visibility_required(view_func):
    """
    Decorator to enforce profile visibility settings.

    This decorator checks if the current user has permission to view a profile
    based on its visibility settings. It should be applied to views that display
    profile information.

    The decorated view must have a 'username' parameter that specifies which
    profile to check.
    """

    @wraps(view_func)
    def _wrapped_view(request, username, *args, **kwargs):
        # Get the User object for the requested username, or raise a 404 if not found
        profile_user = get_object_or_404(User, username=username)

        # Check profile visibility settings
        profile = profile_user.profile
        visibility = profile.profile_visibility

        # Determine if the current user can view this profile
        can_view = False

        # Case 1: Profile owner can always view their own profile
        # Case 2: Admins can always view any profile
        # Case 3: Public profiles are visible to everyone
        # Case 4: Members-only profiles are visible to authenticated users
        if (
            request.user == profile_user
            or request.user.is_staff
            or request.user.is_superuser
            or visibility == "public"
            or (visibility == "members" and request.user.is_authenticated)
        ):
            can_view = True

        # If the user doesn't have permission to view the profile, show a message and redirect
        if not can_view:
            messages.error(request, "You don't have permission to view this profile.")
            return redirect("forum:forum_index")

        # User has permission, proceed with the view
        return view_func(request, username, *args, **kwargs)

    return _wrapped_view
