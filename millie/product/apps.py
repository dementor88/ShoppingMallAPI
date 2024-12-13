from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'millie.product'

    def ready(self):
        import millie.product.signals
