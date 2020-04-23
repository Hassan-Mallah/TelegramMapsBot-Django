from django.apps import AppConfig


class AppNameConfig(AppConfig):
    name = 'YandexBot'

    def ready(self):
        from .models import SearchAreas
        from .bot import main
        from threading import Thread
        Thread(target=main).start()


class YandexbotConfig(AppConfig):
    name = 'YandexBot'
