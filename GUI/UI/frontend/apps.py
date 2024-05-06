"""
Let django know that frontend is a module (an app)
that should be included in the django project
"""
from django.apps import AppConfig


class FrontendConfig(AppConfig):
    """
    default id for the models and name of the app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'
