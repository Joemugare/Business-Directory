from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('businesses/', views.BusinessList.as_view(), name='business_list'),
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('reviews/', views.ReviewList.as_view(), name='review_list'),
]