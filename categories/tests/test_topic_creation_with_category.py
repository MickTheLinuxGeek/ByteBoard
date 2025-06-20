from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from categories.models import Category
from forum.models import Topic, Post

HTTP_SUCCESS = 200


class TestTopicCreationWithCategory(TestCase):
    """Integration tests for topic creation with category selection."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test categories
        self.category1 = Category.objects.create(
            name="Test Category 1",
            description="This is test category 1",
        )
        self.category2 = Category.objects.create(
            name="Test Category 2",
            description="This is test category 2",
        )

        # Set up the test client
        self.client = Client()
        # Log in the test user
        self.client.login(username="testuser", password="testpassword")

    def test_new_topic_form_includes_category_field(self):
        """Test that the new topic form includes a category field."""
        # Access the new topic page
        response = self.client.get(reverse("forum:new_topic"))

        # Check that the page loads successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the form includes a category field
        self.assertContains(response, "Category")
        self.assertContains(response, "Test Category 1")
        self.assertContains(response, "Test Category 2")

    def test_create_topic_with_category(self):
        """Test that a topic can be created with a category."""
        # Create a new topic with category 1
        form_data = {
            "subject": "New Test Topic",
            "message": "This is a new test topic",
            "category": self.category1.id,
        }
        response = self.client.post(reverse("forum:new_topic"), form_data, follow=True)

        # Check that the topic was created successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the topic was created with the correct category
        topic = Topic.objects.get(subject="New Test Topic")
        self.assertEqual(topic.category, self.category1)

        # Check that the initial post was created
        post = Post.objects.get(topic=topic)
        self.assertEqual(post.message, "This is a new test topic")
        self.assertEqual(post.created_by, self.user)

        # Check that the response redirects to the topic detail page
        self.assertContains(response, "New Test Topic")
        self.assertContains(response, "This is a new test topic")
        self.assertContains(response, "Test Category 1")

    def test_create_topic_with_different_category(self):
        """Test that a topic can be created with a different category."""
        # Create a new topic with category 2
        form_data = {
            "subject": "Another Test Topic",
            "message": "This is another test topic",
            "category": self.category2.id,
        }
        response = self.client.post(reverse("forum:new_topic"), form_data, follow=True)

        # Check that the topic was created successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the topic was created with the correct category
        topic = Topic.objects.get(subject="Another Test Topic")
        self.assertEqual(topic.category, self.category2)

        # Check that the response redirects to the topic detail page
        self.assertContains(response, "Another Test Topic")
        self.assertContains(response, "This is another test topic")
        self.assertContains(response, "Test Category 2")

    def test_create_topic_without_category(self):
        """Test that a topic cannot be created without a category."""
        # Try to create a new topic without a category
        form_data = {
            "subject": "Topic Without Category",
            "message": "This topic has no category",
        }
        response = self.client.post(reverse("forum:new_topic"), form_data)

        # Check that the form is invalid and the page is re-rendered
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertContains(response, "This field is required")

        # Check that no topic was created
        self.assertFalse(Topic.objects.filter(subject="Topic Without Category").exists())

    def test_create_topic_with_invalid_category(self):
        """Test that a topic cannot be created with an invalid category."""
        # Try to create a new topic with an invalid category ID
        form_data = {
            "subject": "Topic With Invalid Category",
            "message": "This topic has an invalid category",
            "category": 999,  # Invalid category ID
        }
        response = self.client.post(reverse("forum:new_topic"), form_data)

        # Check that the form is invalid and the page is re-rendered
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        self.assertContains(response, "Select a valid choice")

        # Check that no topic was created
        self.assertFalse(Topic.objects.filter(subject="Topic With Invalid Category").exists())

    def test_topic_creation_requires_login(self):
        """Test that a user must be logged in to create a topic."""
        # Log out the test user
        self.client.logout()

        # Try to access the new topic page
        response = self.client.get(reverse("forum:new_topic"))

        # Check that the user is redirected to the login page
        self.assertNotEqual(response.status_code, HTTP_SUCCESS)
        self.assertIn("login", response.url)

        # Try to create a new topic
        form_data = {
            "subject": "Topic By Anonymous",
            "message": "This topic is created by an anonymous user",
            "category": self.category1.id,
        }
        response = self.client.post(reverse("forum:new_topic"), form_data)

        # Check that the user is redirected to the login page
        self.assertNotEqual(response.status_code, HTTP_SUCCESS)
        self.assertIn("login", response.url)

        # Check that no topic was created
        self.assertFalse(Topic.objects.filter(subject="Topic By Anonymous").exists())