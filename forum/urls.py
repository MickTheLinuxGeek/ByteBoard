# forum/urls.py

from django.urls import path
from . import views # Import views from the current directory (forum app)

# Define a namespace for easier URL referencing in templates (optional but good practice)
app_name = 'forum'

urlpatterns = [
    # Example: /forum/
    path('', views.forum_index, name='forum_index'),

    # Example: /forum/topic/5/  (where 5 is the topic_id)
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # Example: /forum/new_topic/
    path('new_topic/', views.new_topic, name='new_topic'),

    # Example: /forum/topic/5/new_post/
    path('topic/<int:topic_id>/new_post/', views.new_post, name='new_post'),
]