# apps/businesses/urls.py
from django.urls import path
from . import views

app_name = 'businesses'  # This is correct

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('list/', views.BusinessListView.as_view(), name='list'),
    path('search/ajax/', views.business_search_ajax, name='search_ajax'),
    path('create/', views.BusinessCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.BusinessDetailView.as_view(), name='detail'),
    path('update/<slug:slug>/', views.BusinessUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>/', views.BusinessDeleteView.as_view(), name='delete'),
]