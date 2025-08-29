import django_filters
from .models import Business

class BusinessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Business
        fields = ['name', 'address']