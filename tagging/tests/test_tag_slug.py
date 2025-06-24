from django.test import TestCase
from tagging.models import Tag

class TagSlugTest(TestCase):
    """
    Test case for the Tag model's slug generation and normalization.
    """
    
    def test_slug_generation(self):
        """
        Test that a slug is automatically generated from the tag name.
        """
        tag = Tag.objects.create(name="Test Tag")
        self.assertEqual(tag.slug, "test-tag")
        
    def test_custom_slug(self):
        """
        Test that a custom slug can be provided.
        """
        tag = Tag.objects.create(name="Test Tag", slug="custom-slug")
        self.assertEqual(tag.slug, "custom-slug")
        
    def test_name_normalization(self):
        """
        Test that tag names are normalized (converted to lowercase and stripped).
        """
        # Test with uppercase
        tag1 = Tag.objects.create(name="UPPERCASE")
        self.assertEqual(tag1.name, "uppercase")
        
        # Test with leading/trailing whitespace
        tag2 = Tag.objects.create(name="  whitespace  ")
        self.assertEqual(tag2.name, "whitespace")
        
        # Test with mixed case and whitespace
        tag3 = Tag.objects.create(name="  MiXeD CaSe  ")
        self.assertEqual(tag3.name, "mixed case")
        
    def test_slug_from_special_characters(self):
        """
        Test that slugs are properly generated from names with special characters.
        """
        tag = Tag.objects.create(name="Special & Characters!")
        self.assertEqual(tag.slug, "special-characters")
        
    def test_slug_from_multiple_spaces(self):
        """
        Test that slugs are properly generated from names with multiple spaces.
        """
        tag = Tag.objects.create(name="Multiple   Spaces")
        self.assertEqual(tag.slug, "multiple-spaces")