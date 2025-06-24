from django.db import models
from django.utils.text import slugify

# Create your models here.
class Tag(models.Model):
    """
    Model representing a tag that can be applied to posts.
    Tags help in micro-categorization and allow users to find posts 
    related to specific keywords across different topics and categories.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override the save method to normalize the tag name and generate the slug.
        - Converts the name to lowercase
        - Generates a slug from the normalized name
        """
        # Normalize the tag name (convert to lowercase)
        self.name = self.name.lower().strip()

        # Generate slug from the normalized name if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
