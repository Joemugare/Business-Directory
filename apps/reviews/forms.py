from django import forms
from .models import Review
from apps.businesses.models import Business

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['business', 'rating', 'comment']