from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='business_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')  # Added unique related_name
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.business.name} ({self.rating} stars)"