from django.test import TestCase
from django.core.exceptions import ValidationError
from tagging.models import Tag

class TagModelTest(TestCase):
    """
    Test case for the Tag model.
    """
    
    def test_tag_creation(self):
        """
        Test that a tag can be created with valid data.
        """
        tag = Tag.objects.create(name="python")
        self.assertEqual(tag.name, "python")
        self.assertEqual(tag.slug, "python")
        self.assertIsNotNone(tag.created_at)
        
    def test_tag_string_representation(self):
        """
        Test the string representation of a Tag object.
        """
        tag = Tag.objects.create(name="django")
        self.assertEqual(str(tag), "django")
        
    def test_tag_uniqueness(self):
        """
        Test that tags with the same name cannot be created.
        """
        Tag.objects.create(name="unique")
        
        # Try to create another tag with the same name
        with self.assertRaises(Exception):
            Tag.objects.create(name="unique")
            
    def test_tag_slug_uniqueness(self):
        """
        Test that tags with the same slug cannot be created.
        """
        Tag.objects.create(name="first tag", slug="first-tag")
        
        # Try to create another tag with the same slug
        with self.assertRaises(Exception):
            Tag.objects.create(name="different name", slug="first-tag")
            
    def test_tag_name_max_length(self):
        """
        Test that tag names cannot exceed the maximum length.
        """
        # Create a tag with a name that's too long (> 50 characters)
        long_name = "a" * 51
        tag = Tag(name=long_name)
        
        with self.assertRaises(ValidationError):
            tag.full_clean()  # This validates the model fields