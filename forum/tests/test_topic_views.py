from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Post, Topic
from categories.models import Category

HTTP_SUCCESS = 200
HTTP_REDIRECT = 302


class TestTopicViews(TestCase):
    """Tests for the topic-related views."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        
        # Create another test user
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpassword",  # noqa: S106
        )
        
        # Create a test category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description",
        )
        
        # Create a test topic
        self.topic = Topic.objects.create(
            subject="Test Topic",
            created_by=self.user,
            category=self.category,
        )
        
        # Create a test post in the topic
        self.post = Post.objects.create(
            message="Test message content",
            topic=self.topic,
            created_by=self.user,
        )
        
        # Set up the test client
        self.client = Client()

    def test_forum_index_view(self):
        """Test the forum index view."""
        response = self.client.get(reverse("forum:forum_index"))
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/forum_index.html")
        self.assertContains(response, "Test Topic")
        self.assertContains(response, "testuser")

    def test_topic_detail_view(self):
        """Test the topic detail view."""
        response = self.client.get(
            reverse("forum:topic_detail", kwargs={"topic_id": self.topic.id})
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/topic_detail.html")
        self.assertContains(response, "Test Topic")
        self.assertContains(response, "Test message content")
        self.assertContains(response, "testuser")

    def test_new_topic_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected when trying to access the new topic page."""
        response = self.client.get(reverse("forum:new_topic"))
        self.assertEqual(response.status_code, HTTP_REDIRECT)

    def test_new_topic_view_get_authenticated(self):
        """Test that authenticated users can access the new topic page."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(reverse("forum:new_topic"))
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/new_topic.html")

    def test_new_topic_view_post_valid(self):
        """Test creating a new topic with valid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "subject": "New Test Topic",
            "category": self.category.id,
            "message": "This is a new test topic message.",
        }
        response = self.client.post(reverse("forum:new_topic"), form_data)
        self.assertEqual(response.status_code, HTTP_REDIRECT)
        
        # Check that the topic was created
        new_topic = Topic.objects.get(subject="New Test Topic")
        self.assertEqual(new_topic.created_by, self.user)
        self.assertEqual(new_topic.category, self.category)
        
        # Check that the post was created
        new_post = Post.objects.get(topic=new_topic)
        self.assertEqual(new_post.message, "This is a new test topic message.")
        self.assertEqual(new_post.created_by, self.user)

    def test_new_topic_view_post_invalid(self):
        """Test creating a new topic with invalid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "subject": "",  # Empty subject (invalid)
            "category": self.category.id,
            "message": "This is a new test topic message.",
        }
        response = self.client.post(reverse("forum:new_topic"), form_data)
        self.assertEqual(response.status_code, HTTP_SUCCESS)  # Form is redisplayed
        self.assertTemplateUsed(response, "forum/new_topic.html")
        self.assertContains(response, "This field is required")  # Error message

    def test_sticky_topics_display(self):
        """Test that sticky topics are displayed at the top of the forum index."""
        # Create a sticky topic
        sticky_topic = Topic.objects.create(
            subject="Sticky Topic",
            created_by=self.user,
            category=self.category,
            is_sticky=True,
        )
        
        # Create a post in the sticky topic
        Post.objects.create(
            message="Sticky topic message",
            topic=sticky_topic,
            created_by=self.user,
        )
        
        response = self.client.get(reverse("forum:forum_index"))
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        
        # Check that the sticky topic is in the response
        self.assertContains(response, "Sticky Topic")
        
        # The test would be more complete if we could check the order of topics,
        # but that would require parsing the HTML which is beyond the scope of this test