from django.test import TestCase
from django.contrib.auth.models import User
from forum.models import Topic, Post
from tagging.models import Tag

class PostTagRelationshipTest(TestCase):
    """
    Test case for the relationship between Post and Tag models.
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
        
        # Create a topic
        self.topic = Topic.objects.create(
            subject='Test Topic',
            created_by=self.user
        )
        
        # Create a post
        self.post = Post.objects.create(
            message='Test message',
            topic=self.topic,
            created_by=self.user
        )
        
        # Create some tags
        self.tag1 = Tag.objects.create(name='python')
        self.tag2 = Tag.objects.create(name='django')
        self.tag3 = Tag.objects.create(name='testing')
    
    def test_add_tags_to_post(self):
        """
        Test that tags can be added to a post.
        """
        # Add tags to the post
        self.post.tags.add(self.tag1, self.tag2)
        
        # Check that the post has the correct tags
        self.assertEqual(self.post.tags.count(), 2)
        self.assertIn(self.tag1, self.post.tags.all())
        self.assertIn(self.tag2, self.post.tags.all())
        
    def test_remove_tags_from_post(self):
        """
        Test that tags can be removed from a post.
        """
        # Add tags to the post
        self.post.tags.add(self.tag1, self.tag2)
        
        # Remove a tag
        self.post.tags.remove(self.tag1)
        
        # Check that the post has the correct tags
        self.assertEqual(self.post.tags.count(), 1)
        self.assertNotIn(self.tag1, self.post.tags.all())
        self.assertIn(self.tag2, self.post.tags.all())
        
    def test_clear_tags_from_post(self):
        """
        Test that all tags can be cleared from a post.
        """
        # Add tags to the post
        self.post.tags.add(self.tag1, self.tag2, self.tag3)
        
        # Clear all tags
        self.post.tags.clear()
        
        # Check that the post has no tags
        self.assertEqual(self.post.tags.count(), 0)
        
    def test_get_posts_by_tag(self):
        """
        Test that posts can be retrieved by tag.
        """
        # Create another post
        post2 = Post.objects.create(
            message='Another test message',
            topic=self.topic,
            created_by=self.user
        )
        
        # Add tags to the posts
        self.post.tags.add(self.tag1, self.tag2)
        post2.tags.add(self.tag2, self.tag3)
        
        # Get posts with tag1
        posts_with_tag1 = Post.objects.filter(tags=self.tag1)
        self.assertEqual(posts_with_tag1.count(), 1)
        self.assertIn(self.post, posts_with_tag1)
        
        # Get posts with tag2
        posts_with_tag2 = Post.objects.filter(tags=self.tag2)
        self.assertEqual(posts_with_tag2.count(), 2)
        self.assertIn(self.post, posts_with_tag2)
        self.assertIn(post2, posts_with_tag2)
        
    def test_get_tags_by_post(self):
        """
        Test that tags can be retrieved by post.
        """
        # Add tags to the post
        self.post.tags.add(self.tag1, self.tag2)
        
        # Get tags for the post
        tags = self.post.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)