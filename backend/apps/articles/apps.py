from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.articles'

    def ready(self):
        import apps.articles.signals  # noqa
