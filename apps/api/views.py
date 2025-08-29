from rest_framework import generics
from apps.businesses.models import Business
from apps.categories.models import Category
from apps.reviews.models import Review
from .serializers import BusinessSerializer, CategorySerializer, ReviewSerializer

class BusinessList(generics.ListCreateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer