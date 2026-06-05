from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from .utils import init_system_config
        init_system_config()

        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            pass
