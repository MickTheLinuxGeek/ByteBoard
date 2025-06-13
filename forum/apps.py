from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "forum"

    def ready(self):
        """
        Import signals when the app is ready.
        This connects the signal handlers to handle User creation and updates.
        """
        import forum.signals  # noqa
