from django.apps import AppConfig
import os


class MoviesConfig(AppConfig):
    name = 'some_app'

    def ready(self):
        print(' .---------------------- --- --')
        print(os.getpid())
