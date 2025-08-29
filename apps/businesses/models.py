from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Avg
from django.urls import reverse

class Business(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    featured_image = models.ImageField(upload_to='images/', blank=True, null=True)
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, related_name='businesses')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_businesses')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Business.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def average_rating(self):
        approved_reviews = self.business_reviews.filter(is_approved=True)
        if approved_reviews.exists():
            return approved_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return 0

    def total_reviews(self):
        return self.business_reviews.filter(is_approved=True).count()

    def get_absolute_url(self):
        return reverse('businesses:detail', kwargs={'slug': self.slug})
