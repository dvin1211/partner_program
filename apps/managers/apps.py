from django.apps import AppConfig


class ManagersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.managers'
    verbose_name = 'Менеджеры'

    def ready(self):
        import apps.managers.signals