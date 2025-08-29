from django.contrib import admin
from .models import Business

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'is_active', 'is_featured', 'is_verified', 'created_at')
    search_fields = ('name', 'description', 'address', 'city')
    list_filter = ('category', 'is_active', 'is_featured', 'is_verified')
    ordering = ('-created_at',)
    prepopulated_fields = {"slug": ("name",)}  # auto-generate slug from name