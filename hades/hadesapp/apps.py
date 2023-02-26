from django.apps import AppConfig


class HadesappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hadesapp'
    def ready(self):
        import hadesapp.signals
