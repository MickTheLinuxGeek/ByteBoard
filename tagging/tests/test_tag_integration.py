from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from forum.models import Topic, Post
from tagging.models import Tag
from categories.models import Category

class TagCreationDuringPostTest(TestCase):
    """
    Integration tests for tag creation during post creation and editing.
    """

    def setUp(self):
        """
        Set up test data.
        """
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )

        # Create a topic
        self.topic = Topic.objects.create(
            subject='Test Topic',
            created_by=self.user,
            category=self.category
        )

        # Create a post
        self.post = Post.objects.create(
            message='Test message',
            topic=self.topic,
            created_by=self.user
        )

        # Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_tag_creation_during_new_topic(self):
        """
        Test that tags are created when creating a new topic.
        """
        # Data for the new topic
        topic_data = {
            'subject': 'New Topic with Tags',
            'category': self.category.id,
            'message': 'This is a test message for a new topic with tags.',
            'tags': 'python, django, testing'
        }

        # Submit the form to create a new topic
        response = self.client.post(reverse('forum:new_topic'), topic_data, follow=True)

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Get the newly created topic
        new_topic = Topic.objects.get(subject='New Topic with Tags')

        # Get the post associated with the new topic
        new_post = Post.objects.get(topic=new_topic)

        # Check that the tags were created and associated with the post
        self.assertEqual(new_post.tags.count(), 3)
        self.assertTrue(new_post.tags.filter(name='python').exists())
        self.assertTrue(new_post.tags.filter(name='django').exists())
        self.assertTrue(new_post.tags.filter(name='testing').exists())

    def test_tag_creation_during_new_post(self):
        """
        Test that tags are created when creating a new post (reply).
        """
        # Data for the new post
        post_data = {
            'message': 'This is a test reply with tags.',
            'tags': 'reply, test, integration'
        }

        # Submit the form to create a new post
        response = self.client.post(
            reverse('forum:new_post', kwargs={'topic_id': self.topic.id}),
            post_data,
            follow=True
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Get the newly created post
        new_post = Post.objects.get(message='This is a test reply with tags.')

        # Check that the tags were created and associated with the post
        self.assertEqual(new_post.tags.count(), 3)
        self.assertTrue(new_post.tags.filter(name='reply').exists())
        self.assertTrue(new_post.tags.filter(name='test').exists())
        self.assertTrue(new_post.tags.filter(name='integration').exists())

    def test_tag_update_during_post_edit(self):
        """
        Test that tags are updated when editing a post.
        """
        # Add some initial tags to the post
        tag1 = Tag.objects.create(name='initial')
        tag2 = Tag.objects.create(name='tags')
        self.post.tags.add(tag1, tag2)

        # Data for editing the post
        edit_data = {
            'message': 'Updated test message',
            'tags': 'updated, tags, edit'
        }

        # Submit the form to edit the post
        response = self.client.post(
            reverse('forum:edit_post', kwargs={'post_id': self.post.id}),
            edit_data,
            follow=True
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Refresh the post from the database
        self.post.refresh_from_db()

        # Check that the post message was updated
        self.assertEqual(self.post.message, 'Updated test message')

        # Check that the tags were updated
        self.assertEqual(self.post.tags.count(), 3)
        self.assertTrue(self.post.tags.filter(name='updated').exists())
        self.assertTrue(self.post.tags.filter(name='tags').exists())
        self.assertTrue(self.post.tags.filter(name='edit').exists())
        self.assertFalse(self.post.tags.filter(name='initial').exists())

    def test_tag_normalization(self):
        """
        Test that tags are normalized (lowercase, trimmed) during post creation.
        """
        # Data for the new post with tags that need normalization
        post_data = {
            'message': 'This is a test post for tag normalization.',
            'tags': ' Python , DJANGO,  testing '
        }

        # Submit the form to create a new post
        response = self.client.post(
            reverse('forum:new_post', kwargs={'topic_id': self.topic.id}),
            post_data,
            follow=True
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Get the newly created post
        new_post = Post.objects.get(message='This is a test post for tag normalization.')

        # Check that the tags were normalized
        self.assertEqual(new_post.tags.count(), 3)
        self.assertTrue(new_post.tags.filter(name='python').exists())
        self.assertTrue(new_post.tags.filter(name='django').exists())
        self.assertTrue(new_post.tags.filter(name='testing').exists())

        # Check that the original case and spacing is not preserved
        self.assertFalse(new_post.tags.filter(name='Python').exists())
        self.assertFalse(new_post.tags.filter(name='DJANGO').exists())
        self.assertFalse(new_post.tags.filter(name=' testing ').exists())


class PostsByTagTest(TestCase):
    """
    Integration tests for the posts by tag functionality.
    """

    def setUp(self):
        """
        Set up test data.
        """
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password1'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password2'
        )

        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )

        # Create topics
        self.topic1 = Topic.objects.create(
            subject='Topic 1',
            created_by=self.user1,
            category=self.category
        )

        self.topic2 = Topic.objects.create(
            subject='Topic 2',
            created_by=self.user2,
            category=self.category
        )

        # Create tags
        self.tag_python = Tag.objects.create(name='python')
        self.tag_django = Tag.objects.create(name='django')
        self.tag_testing = Tag.objects.create(name='testing')

        # Create posts with tags
        self.post1 = Post.objects.create(
            message='Post 1 about Python and Django',
            topic=self.topic1,
            created_by=self.user1
        )
        self.post1.tags.add(self.tag_python, self.tag_django)

        self.post2 = Post.objects.create(
            message='Post 2 about Python and Testing',
            topic=self.topic1,
            created_by=self.user1
        )
        self.post2.tags.add(self.tag_python, self.tag_testing)

        self.post3 = Post.objects.create(
            message='Post 3 about Django only',
            topic=self.topic2,
            created_by=self.user2
        )
        self.post3.tags.add(self.tag_django)

        # Create a client
        self.client = Client()

    def test_posts_by_tag_view(self):
        """
        Test that the posts by tag view displays the correct posts.
        """
        # Get posts by the 'python' tag
        response = self.client.get(reverse('tagging:posts_by_tag', kwargs={'tag_slug': 'python'}))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'tagging/posts_by_tag.html')

        # Check that the tag is in the context
        self.assertEqual(response.context['tag'], self.tag_python)

        # Check that the correct posts are in the context
        posts = response.context['posts']
        self.assertEqual(posts.paginator.count, 2)  # 2 posts with the 'python' tag
        self.assertIn(self.post1, posts.object_list)
        self.assertIn(self.post2, posts.object_list)
        self.assertNotIn(self.post3, posts.object_list)

    def test_posts_by_tag_pagination(self):
        """
        Test that the posts by tag view paginates correctly.
        """
        # Create 10 more posts with the 'python' tag
        for i in range(10):
            post = Post.objects.create(
                message=f'Additional post {i+1} about Python',
                topic=self.topic1,
                created_by=self.user1
            )
            post.tags.add(self.tag_python)

        # Get the first page of posts by the 'python' tag
        response = self.client.get(reverse('tagging:posts_by_tag', kwargs={'tag_slug': 'python'}))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the posts are paginated
        posts = response.context['posts']
        self.assertEqual(posts.paginator.count, 12)  # 12 posts with the 'python' tag
        self.assertEqual(len(posts.object_list), 10)  # 10 posts per page

        # Get the second page
        response = self.client.get(reverse('tagging:posts_by_tag', kwargs={'tag_slug': 'python'}) + '?page=2')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the second page has the remaining posts
        posts = response.context['posts']
        self.assertEqual(len(posts.object_list), 2)  # 2 posts on the second page

    def test_posts_by_nonexistent_tag(self):
        """
        Test that the posts by tag view returns a 404 for a nonexistent tag.
        """
        response = self.client.get(reverse('tagging:posts_by_tag', kwargs={'tag_slug': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)


class TagSuggestionsTest(TestCase):
    """
    Integration tests for the tag suggestions/autocomplete functionality.
    """

    def setUp(self):
        """
        Set up test data.
        """
        # Create tags
        Tag.objects.create(name='python')
        Tag.objects.create(name='django')
        Tag.objects.create(name='flask')
        Tag.objects.create(name='pyramid')
        Tag.objects.create(name='programming')
        Tag.objects.create(name='web-development')

        # Create a client
        self.client = Client()

    def test_tag_suggestions(self):
        """
        Test that the tag suggestions view returns the correct tags.
        """
        # Get suggestions for 'py'
        response = self.client.get(reverse('tagging:tag_suggestions') + '?query=py')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the response is JSON
        self.assertEqual(response['Content-Type'], 'application/json')

        # Check that the correct tags are returned
        data = response.json()
        self.assertIn('tags', data)
        self.assertEqual(len(data['tags']), 2)  # python, pyramid
        self.assertIn('python', data['tags'])
        self.assertIn('pyramid', data['tags'])

    def test_tag_suggestions_empty_query(self):
        """
        Test that the tag suggestions view returns an empty list for an empty query.
        """
        # Get suggestions for an empty query
        response = self.client.get(reverse('tagging:tag_suggestions') + '?query=')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that an empty list is returned
        data = response.json()
        self.assertIn('tags', data)
        self.assertEqual(len(data['tags']), 0)

    def test_tag_suggestions_case_insensitive(self):
        """
        Test that the tag suggestions view is case-insensitive.
        """
        # Get suggestions for 'PY' (uppercase)
        response = self.client.get(reverse('tagging:tag_suggestions') + '?query=PY')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the correct tags are returned (case-insensitive)
        data = response.json()
        self.assertIn('tags', data)
        self.assertEqual(len(data['tags']), 2)  # python, pyramid
        self.assertIn('python', data['tags'])
        self.assertIn('pyramid', data['tags'])

    def test_tag_suggestions_limit(self):
        """
        Test that the tag suggestions view limits the number of results.
        """
        # Create 20 more tags with names starting with 'test'
        for i in range(20):
            Tag.objects.create(name=f'test{i}')

        # Get suggestions for 'test'
        response = self.client.get(reverse('tagging:tag_suggestions') + '?query=test')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the number of results is limited to 10
        data = response.json()
        self.assertIn('tags', data)
        self.assertEqual(len(data['tags']), 10)
