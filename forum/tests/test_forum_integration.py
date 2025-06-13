from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from forum.models import Post, Profile, Topic

HTTP_SUCCESS = 200


class TestForumIntegration(TestCase):
    """Integration tests for forum features that integrate with user profiles."""

    def setUp(self):
        """Set up test data."""
        # Create a test user with a profile
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",  # noqa: S106
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile.bio = "Test bio"
        self.profile.signature = "Test signature"
        self.profile.user_title = "Test User Title"
        self.profile.save()

        # Create a second user
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpassword",  # noqa: S106
        )

        # Create a topic and posts
        self.topic = Topic.objects.create(
            subject="Test Topic",
            created_by=self.user,
        )

        self.post1 = Post.objects.create(
            message="Test post 1",
            topic=self.topic,
            created_by=self.user,
        )

        self.post2 = Post.objects.create(
            message="Test post 2",
            topic=self.topic,
            created_by=self.other_user,
        )

        # Set up the test client
        self.client = Client()

    def test_avatar_display_in_topic_list(self):
        """Test that avatars are displayed next to topic creators in the forum index."""
        # Access the forum index
        response = self.client.get(reverse("forum:forum_index"))

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the avatar URL is included in the response
        self.assertContains(response, self.profile.get_avatar_url())

        # Check that the topic creator's username is displayed
        self.assertContains(response, self.user.username)

    def test_avatar_display_in_topic_detail(self):
        """Test that avatars are displayed next to posts in the topic detail view."""
        # Access the topic detail page
        response = self.client.get(
            reverse("forum:topic_detail", kwargs={"topic_id": self.topic.id}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the avatar URLs are included in the response
        self.assertContains(response, self.profile.get_avatar_url())
        self.assertContains(
            response,
            Profile.objects.get(user=self.other_user).get_avatar_url(),
        )

        # Check that the post creators' usernames are displayed
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.other_user.username)

    def test_signature_display_in_posts(self):
        """Test that user signatures are displayed at the bottom of their posts."""
        # Access the topic detail page
        response = self.client.get(
            reverse("forum:topic_detail", kwargs={"topic_id": self.topic.id}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the signature is included in the response
        self.assertContains(response, "Test signature")

    def test_user_title_display(self):
        """Test that user titles are displayed next to usernames."""
        # Access the topic detail page
        response = self.client.get(
            reverse("forum:topic_detail", kwargs={"topic_id": self.topic.id}),
        )

        # Check that the page loads successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the user title is included in the response
        self.assertContains(response, "Test User Title")

    def test_last_seen_tracking(self):
        """Test that the last_seen field is updated when a user interacts with the site."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Record the current last_seen value
        self.profile.refresh_from_db()
        old_last_seen = self.profile.last_seen

        # Make a request to the site
        self.client.get(reverse("forum:forum_index"))

        # Check that the last_seen field was updated
        self.profile.refresh_from_db()
        assert self.profile.last_seen is not None  # noqa: S101
        if old_last_seen:
            assert self.profile.last_seen > old_last_seen  # noqa: S101

    def test_new_topic_with_signature(self):
        """Test that when a user creates a new topic, their signature is displayed with the post."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Create a new topic
        form_data = {
            "subject": "New Test Topic",
            "message": "This is a new test topic",
        }
        response = self.client.post(reverse("forum:new_topic"), form_data, follow=True)

        # Check that the topic was created successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the signature is included in the response
        self.assertContains(response, "Test signature")

    def test_new_post_with_signature(self):
        """Test that when a user creates a new post, their signature is displayed with it."""
        # Log in as the test user
        self.client.login(username="testuser", password="testpassword")  # noqa: S106

        # Create a new post
        form_data = {
            "message": "This is a new test post",
        }
        response = self.client.post(
            reverse("forum:new_post", kwargs={"topic_id": self.topic.id}),
            form_data,
            follow=True,
        )

        # Check that the post was created successfully
        assert response.status_code == HTTP_SUCCESS  # noqa: S101

        # Check that the signature is included in the response
        self.assertContains(response, "Test signature")
