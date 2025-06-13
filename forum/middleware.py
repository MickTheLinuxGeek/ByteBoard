# forum/middleware.py

from django.utils import timezone


class LastSeenMiddleware:
    """Middleware to update the 'last_seen' field in the user's profile whenever they make a request to the site."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Update last_seen for authenticated users
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            # Update the last_seen field with the current time
            # Only update if the user has a profile
            request.user.profile.last_seen = timezone.now()
            request.user.profile.save(update_fields=["last_seen"])

        return response
