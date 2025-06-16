from django.test import Client, TestCase
from django.urls import reverse
from django.core.paginator import Page

from categories.models import Category

HTTP_SUCCESS = 200


class TestCategoryListing(TestCase):
    """Integration tests for category listing functionality."""

    def setUp(self):
        """Set up test data."""
        # Create multiple test categories
        self.category1 = Category.objects.create(
            name="Test Category 1",
            description="This is test category 1",
        )
        self.category2 = Category.objects.create(
            name="Test Category 2",
            description="This is test category 2",
        )
        self.category3 = Category.objects.create(
            name="Test Category 3",
            description="This is test category 3",
        )

        # Set up the test client
        self.client = Client()

    def test_category_list_view(self):
        """Test that the category list view displays all categories."""
        # Access the category list view
        response = self.client.get(reverse("categories:category_list"))

        # Check that the page loads successfully
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that all categories are included in the response
        self.assertContains(response, "Test Category 1")
        self.assertContains(response, "Test Category 2")
        self.assertContains(response, "Test Category 3")
        self.assertContains(response, "This is test category 1")
        self.assertContains(response, "This is test category 2")
        self.assertContains(response, "This is test category 3")

    def test_category_list_pagination(self):
        """Test that the category list view paginates correctly."""
        # Create more categories to trigger pagination (10 per page)
        for i in range(4, 15):  # Create 11 more categories for a total of 14
            Category.objects.create(
                name=f"Test Category {i}",
                description=f"This is test category {i}",
            )

        # Access the category list view (first page)
        response = self.client.get(reverse("categories:category_list"))
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the response contains a Page object
        self.assertIsInstance(response.context["categories"], Page)

        # Check that the first page has 10 categories
        self.assertEqual(len(response.context["categories"]), 10)

        # Get the category names from the first page
        first_page_categories = [category.name for category in response.context["categories"]]

        # Access the second page
        response = self.client.get(reverse("categories:category_list") + "?page=2")
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the second page has the remaining 4 categories
        self.assertEqual(len(response.context["categories"]), 4)

        # Get the category names from the second page
        second_page_categories = [category.name for category in response.context["categories"]]

        # Check that there's no overlap between the first and second pages
        for category_name in first_page_categories:
            self.assertNotIn(category_name, second_page_categories)

        for category_name in second_page_categories:
            self.assertNotIn(category_name, first_page_categories)

        # Check that all 14 categories are accounted for
        all_categories = first_page_categories + second_page_categories
        self.assertEqual(len(all_categories), 14)

        # Check that all expected categories are in the combined list
        for i in range(1, 15):
            self.assertIn(f"Test Category {i}", all_categories)

    def test_category_list_invalid_page(self):
        """Test that requesting an invalid page returns the first page."""
        # Access the category list view with an invalid page number
        response = self.client.get(reverse("categories:category_list") + "?page=999")
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the response contains the last page
        self.assertContains(response, "Test Category 1")
        self.assertContains(response, "Test Category 2")
        self.assertContains(response, "Test Category 3")

    def test_category_list_non_integer_page(self):
        """Test that requesting a non-integer page returns the first page."""
        # Access the category list view with a non-integer page number
        response = self.client.get(reverse("categories:category_list") + "?page=abc")
        self.assertEqual(response.status_code, HTTP_SUCCESS)

        # Check that the response contains the first page
        self.assertContains(response, "Test Category 1")
        self.assertContains(response, "Test Category 2")
        self.assertContains(response, "Test Category 3")
