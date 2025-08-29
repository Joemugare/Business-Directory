# apps/categories/apps.py
from django.apps import AppConfig

class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.categories'  # Full path to the app
    label = 'categories'      # Unique label for the app