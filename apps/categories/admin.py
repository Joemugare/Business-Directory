from django.contrib import admin
from .models import Category
from apps.businesses.models import Business

class BusinessInline(admin.TabularInline):   # or StackedInline for bigger forms
    model = Business
    extra = 1   # how many empty forms to show by default

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    search_fields = ('name', 'description')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BusinessInline]   # attach businesses inline
