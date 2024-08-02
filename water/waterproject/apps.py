from django.apps import AppConfig


class WaterProjectConfig(AppConfig):
    name = 'waterproject'

    def ready(self):
        import waterproject.signals
