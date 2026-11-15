from django.apps import AppConfig


class NotFoundPageConfig(AppConfig):
    name = "notfound_page"
    verbose_name = "Not Found Page"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import checks  # noqa: F401  (registers system checks)
