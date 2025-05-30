from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw


class Command(BaseCommand):
    help = "Creates a default avatar image"

    def handle(self, *args, **options):
        # Define the path for the default avatar
        avatar_dir = Path(settings.BASE_DIR) / "forum" / "static" / "forum" / "images"
        # avatar_dir = os.path.join(settings.BASE_DIR, "forum", "static", "forum", "images")
        avatar_path = avatar_dir / "default_avatar.png"
        # avatar_path = os.path.join(avatar_dir, "default_avatar.png")

        # Create directory if it doesn't exist
        Path(avatar_dir).mkdir(parents=True, exist_ok=True)
        # os.makedirs(avatar_dir, exist_ok=True)

        # Create a 200x200 image with a blue background
        size = (200, 200)
        img: Image = Image.new("RGB", size, color=(73, 109, 137))

        # Get a drawing context
        d = ImageDraw.Draw(img)

        # Draw a simple avatar (a circle)
        d.ellipse((50, 50, 150, 150), fill=(255, 255, 255))

        # Save the image
        img.save(avatar_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully created default avatar at {avatar_path}"))
