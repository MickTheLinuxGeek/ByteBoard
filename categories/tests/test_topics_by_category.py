from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Page

from categories.models import Category
from forum.models import Topic

HTTP_SUCCESS = 200


class TestTopicsByCategory(TestCase):
    """Integration tests for topics by category functionality."""

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

        # Create test topics in category 1
        self.topic1 = Topic.objects.create(
            subject="Test Topic 1",
            created_by=self.user,
            category=self.category1,
        )
        self.topic2 = Topic.objects.create(
            subject="Test Topic 2",
            created_by=self.user,
            category=self.category1,
        )
        self.sticky_topic = Topic.objects.create(
            subject="Sticky Topic",
            created_by=self.user,
            category=self.category1,
            is_sticky=True,
        )

        # Create test topics in category 2
        self.topic3 = Topic.objects.create(
            subject="Test Topic 3",
            created_by=self.user,
            category=self.category2,
        )

        # Set up the test client
        self.client = Client()

    def test_topics_by_category_view(self):
        """Test that the topics by category view displays topics for the correct category."""
        # Access the topics by category view for category 1
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug})
        )

        # Check that the page loads successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the category information is included in the response
        self.assertContains(response, "Test Category 1")
        self.assertContains(response, "This is test category 1")

        # Check that topics from category 1 are included in the response
        self.assertContains(response, "Test Topic 1")
        self.assertContains(response, "Test Topic 2")
        self.assertContains(response, "Sticky Topic")

        # Check that topics from category 2 are not included in the response
        self.assertNotContains(response, "Test Topic 3")

        # Access the topics by category view for category 2
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category2.slug})
        )

        # Check that the page loads successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the category information is included in the response
        self.assertContains(response, "Test Category 2")
        self.assertContains(response, "This is test category 2")

        # Check that topics from category 2 are included in the response
        self.assertContains(response, "Test Topic 3")

        # Check that topics from category 1 are not included in the response
        self.assertNotContains(response, "Test Topic 1")
        self.assertNotContains(response, "Test Topic 2")
        self.assertNotContains(response, "Sticky Topic")

    def test_sticky_topics_display(self):
        """Test that sticky topics are displayed at the top of the topics list."""
        # Access the topics by category view for category 1
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug})
        )

        # Check that the page loads successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that sticky topics are included in the context
        self.assertIn("sticky_topics", response.context)
        self.assertEqual(len(response.context["sticky_topics"]), 1)
        self.assertEqual(response.context["sticky_topics"][0].subject, "Sticky Topic")

        # Check that regular topics are included in the context
        self.assertIn("regular_topics_page", response.context)
        self.assertEqual(len(response.context["regular_topics_page"]), 2)

    def test_topics_by_category_pagination(self):
        """Test that the topics by category view paginates correctly."""
        # Create more topics in category 1 to trigger pagination (5 per page)
        for i in range(3, 10):  # Create 7 more topics for a total of 9 regular topics
            Topic.objects.create(
                subject=f"Test Topic {i}",
                created_by=self.user,
                category=self.category1,
            )

        # Access the topics by category view for category 1 (first page)
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug})
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the response contains a Page object for regular topics
        self.assertIsInstance(response.context["regular_topics_page"], Page)
        
        # Check that the first page has 5 regular topics
        self.assertEqual(len(response.context["regular_topics_page"]), 5)
        
        # Check that sticky topics are still displayed
        self.assertEqual(len(response.context["sticky_topics"]), 1)
        
        # Access the second page
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug}) + "?page=2"
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        
        # Check that the second page has the remaining 4 regular topics
        self.assertEqual(len(response.context["regular_topics_page"]), 4)
        
        # Check that sticky topics are still displayed on the second page
        self.assertEqual(len(response.context["sticky_topics"]), 1)

    def test_topics_by_category_invalid_category(self):
        """Test that requesting an invalid category returns a 404 error."""
        # Access the topics by category view with an invalid category slug
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": "invalid-category"})
        )
        self.assertEqual(response.status_code, 404)

    def test_topics_by_category_invalid_page(self):
        """Test that requesting an invalid page returns the last page."""
        # Access the topics by category view with an invalid page number
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug}) + "?page=999"
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        
        # Check that the response contains the last page
        self.assertContains(response, "Test Topic 1")
        self.assertContains(response, "Test Topic 2")

    def test_topics_by_category_non_integer_page(self):
        """Test that requesting a non-integer page returns the first page."""
        # Access the topics by category view with a non-integer page number
        response = self.client.get(
            reverse("categories:topics_by_category", kwargs={"category_slug": self.category1.slug}) + "?page=abc"
        )
        self.assertEqual(response.status_code, HTTP_SUCCESS)
        
        # Check that the response contains the first page
        self.assertContains(response, "Test Topic 1")
        self.assertContains(response, "Test Topic 2")