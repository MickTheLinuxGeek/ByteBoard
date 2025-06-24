from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

from tagging.models import Tag
from forum.models import Topic, Post


class TestTagUIUX(TestCase):
    """UI/UX tests for tagging functionality."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test tags
        self.tag1 = Tag.objects.create(
            name="python",
            slug="python",
        )
        self.tag2 = Tag.objects.create(
            name="django",
            slug="django",
        )
        self.tag3 = Tag.objects.create(
            name="testing",
            slug="testing",
        )

        # Create a test topic
        self.topic = Topic.objects.create(
            subject="Test Topic",
            created_by=self.user,
        )

        # Create test posts with tags
        self.post1 = Post.objects.create(
            message="This is a test post with Python and Django tags.",
            topic=self.topic,
            created_by=self.user,
        )
        self.post1.tags.add(self.tag1, self.tag2)

        self.post2 = Post.objects.create(
            message="This is a test post with Testing tag.",
            topic=self.topic,
            created_by=self.user,
        )
        self.post2.tags.add(self.tag3)

        # Set up the test client
        self.client = Client()
        # Log in the test user
        self.client.login(username="testuser", password="testpassword")

    def test_tag_display_on_posts(self):
        """Test that tags are displayed properly on posts (Task 7.3.1)."""
        # Access the topic detail view
        response = self.client.get(reverse("forum:topic_detail", args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all post divs
        posts = soup.select(".post")
        self.assertEqual(len(posts), 2)

        # Check that the first post has the correct tags
        post1_tags = posts[0].select(".post-tags .tag-item")
        self.assertEqual(len(post1_tags), 2)
        tag_names = [tag.select_one(".tag-name").text for tag in post1_tags]
        self.assertIn("python", tag_names)
        self.assertIn("django", tag_names)

        # Check that the second post has the correct tag
        post2_tags = posts[1].select(".post-tags .tag-item")
        self.assertEqual(len(post2_tags), 1)
        self.assertEqual(post2_tags[0].select_one(".tag-name").text, "testing")

        # Check that tag links point to the correct URL
        for tag_item in post1_tags:
            tag_link = tag_item.select_one("a")["href"]
            tag_name = tag_item.select_one(".tag-name").text
            tag_slug = tag_name  # In this case, the slug is the same as the name
            self.assertIn(f"/tags/{tag_slug}/", tag_link)

    def test_tag_input_functionality(self):
        """Test tag input functionality when creating/editing posts (Task 7.3.2)."""
        # Access the new post form
        response = self.client.get(reverse("forum:new_post", args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check that the tag input field exists
        tag_input = soup.select_one(".tag-input")
        self.assertIsNotNone(tag_input)
        self.assertEqual(tag_input["placeholder"], "Enter tags separated by commas")

        # Check that the tag-autocomplete.js script is included
        script_tags = soup.select("script")
        script_srcs = [script.get("src", "") for script in script_tags]
        self.assertTrue(any("tag-autocomplete.js" in src for src in script_srcs))

        # Test submitting a post with tags
        response = self.client.post(
            reverse("forum:new_post", args=[self.topic.id]),
            {
                "message": "This is a new post with tags.",
                "tags": "python, new-tag",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check that the post was created with the correct tags
        new_post = Post.objects.latest("created_at")
        self.assertEqual(new_post.message, "This is a new post with tags.")
        self.assertEqual(new_post.tags.count(), 2)
        tag_names = [tag.name for tag in new_post.tags.all()]
        self.assertIn("python", tag_names)
        self.assertIn("new-tag", tag_names)

    def test_responsive_design(self):
        """Test responsive design for tag-related pages (Task 7.3.3)."""
        # Test tag list page
        response = self.client.get(reverse("tagging:tag_list"))
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for responsive meta tag in the head
        meta_viewport = soup.select_one('meta[name="viewport"]')
        self.assertIsNotNone(meta_viewport, "Viewport meta tag is missing")
        if meta_viewport:
            self.assertIn("width=device-width", meta_viewport.get("content", ""))

        # Check for responsive CSS elements
        tag_list = soup.select_one(".tag-list")
        self.assertIsNotNone(tag_list, "Tag list container is missing")

        # Test posts by tag page
        response = self.client.get(
            reverse("tagging:posts_by_tag", kwargs={"tag_slug": self.tag1.slug})
        )
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check that the page has the correct title
        self.assertIn(f'Posts tagged with "{self.tag1.name}"', soup.title.text)

        # Check that posts with the tag are displayed
        posts = soup.select(".post")
        self.assertGreaterEqual(len(posts), 1)

        # Check for responsive layout
        meta_viewport = soup.select_one('meta[name="viewport"]')
        self.assertIsNotNone(meta_viewport, "Viewport meta tag is missing")
        if meta_viewport:
            self.assertIn("width=device-width", meta_viewport.get("content", ""))