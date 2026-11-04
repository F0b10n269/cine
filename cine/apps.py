from django.apps import AppConfig


class CineConfig(AppConfig):
    name = 'cine'

    def ready(self):
        from . import signals
