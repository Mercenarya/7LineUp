from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Import the database module to create tables
        from . import database
        # Create all tables defined in the database module
        database.Base.metadata.create_all(database.engine)