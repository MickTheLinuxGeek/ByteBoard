from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from forum.models import Post, Topic
from categories.models import Category

HTTP_SUCCESS = 200
HTTP_REDIRECT = 302
HTTP_FORBIDDEN = 403


class TestPostViews(TestCase):
    """Tests for the post-related views."""

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
        
        # Create another post by the other user
        self.other_post = Post.objects.create(
            message="Another test message",
            topic=self.topic,
            created_by=self.other_user,
        )
        
        # Set up the test client
        self.client = Client()

    def test_new_post_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected when trying to access the new post page."""
        response = self.client.get(
            reverse("forum:new_post", kwargs={"topic_id": self.topic.id})
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)

    def test_new_post_view_get_authenticated(self):
        """Test that authenticated users can access the new post page."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:new_post", kwargs={"topic_id": self.topic.id})
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/new_post.html")

    def test_new_post_view_post_valid(self):
        """Test creating a new post with valid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "message": "This is a new test reply.",
        }
        response = self.client.post(
            reverse("forum:new_post", kwargs={"topic_id": self.topic.id}),
            form_data,
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)
        
        # Check that the post was created
        new_post = Post.objects.filter(message="This is a new test reply.").first()
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.topic, self.topic)
        self.assertEqual(new_post.created_by, self.user)

    def test_new_post_view_post_invalid(self):
        """Test creating a new post with invalid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "message": "",  # Empty message (invalid)
        }
        response = self.client.post(
            reverse("forum:new_post", kwargs={"topic_id": self.topic.id}),
            form_data,
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)  # Form is redisplayed
        self.assertTemplateUsed(response, "forum/new_post.html")
        self.assertContains(response, "This field is required")  # Error message

    def test_edit_post_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected when trying to access the edit post page."""
        response = self.client.get(
            reverse("forum:edit_post", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)

    def test_edit_post_view_get_authenticated_own_post(self):
        """Test that authenticated users can access the edit page for their own posts."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:edit_post", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/edit_post.html")
        self.assertContains(response, "Test message content")  # Original message

    def test_edit_post_view_get_authenticated_other_post(self):
        """Test that authenticated users cannot edit posts they don't own."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:edit_post", kwargs={"post_id": self.other_post.id})
        )
        self.assertEqual(response.status_code, HTTP_FORBIDDEN)

    def test_edit_post_view_post_valid(self):
        """Test editing a post with valid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "message": "Updated test message content",
        }
        response = self.client.post(
            reverse("forum:edit_post", kwargs={"post_id": self.post.id}),
            form_data,
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)
        
        # Check that the post was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.message, "Updated test message content")
        self.assertIsNotNone(self.post.updated_at)

    def test_edit_post_view_post_invalid(self):
        """Test editing a post with invalid data."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        form_data = {
            "message": "",  # Empty message (invalid)
        }
        response = self.client.post(
            reverse("forum:edit_post", kwargs={"post_id": self.post.id}),
            form_data,
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)  # Form is redisplayed
        self.assertTemplateUsed(response, "forum/edit_post.html")
        self.assertContains(response, "This field is required")  # Error message

    def test_delete_post_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected when trying to access the delete post page."""
        response = self.client.get(
            reverse("forum:delete_post", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)

    def test_delete_post_view_get_authenticated_own_post(self):
        """Test that authenticated users can access the delete confirmation page for their own posts."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:delete_post", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertTemplateUsed(response, "forum/delete_post_confirm.html")

    def test_delete_post_view_get_authenticated_other_post(self):
        """Test that authenticated users cannot delete posts they don't own."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        response = self.client.get(
            reverse("forum:delete_post", kwargs={"post_id": self.other_post.id})
        )
        # The view redirects with an error message rather than returning a 403
        self.assertEqual(response.status_code, HTTP_REDIRECT)

    def test_delete_post_view_post(self):
        """Test deleting a post."""
        self.client.login(username="testuser", password="testpassword")  # noqa: S106
        post_id = self.post.id
        response = self.client.post(
            reverse("forum:delete_post", kwargs={"post_id": post_id})
        )
        self.assertEqual(response.status_code, HTTP_REDIRECT)
        
        # Check that the post was deleted
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=post_id)