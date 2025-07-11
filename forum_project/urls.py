"""
URL configuration for forum_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# Import include
from django.urls import include, path

from forum import views as forum_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Add this line: directs URLs starting with 'forum/' to the forum app's urls.py
    path("forum/", include("forum.urls")),
    # Add the signup URL
    path("accounts/signup/", forum_views.signup, name="signup"),  # Map to our new view
    # We could add a path for the homepage later if needed
    path("", forum_views.forum_index, name="home"),
    # Add this line to include Django's built-in authentication URLs
    # under the '/accounts/' path (e.g., /accounts/login/, /accounts/logout/)
    path("accounts/", include("django.contrib.auth.urls")),
    # Add this line to include the categories app URLs
    path("categories/", include("categories.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
