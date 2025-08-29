# apps/businesses/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Business, Category


class BusinessSitemap(Sitemap):
    """Sitemap for individual business listings"""
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'  # Use HTTPS if your site supports it
    
    def items(self):
        # Return all active/published businesses
        return Business.objects.filter(is_active=True, is_approved=True)
    
    def lastmod(self, obj):
        # Return the last modified date
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        # Return the URL for each business
        return reverse('business_detail', kwargs={'pk': obj.pk, 'slug': obj.slug})
    
    def changefreq(self, obj):
        # You can customize change frequency per object
        if obj.is_featured:
            return "daily"
        return "weekly"
    
    def priority(self, obj):
        # You can customize priority per object
        if obj.is_featured:
            return 1.0
        return 0.8


class CategorySitemap(Sitemap):
    """Sitemap for business categories"""
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        # Return all active categories that have businesses
        return Category.objects.filter(
            is_active=True,
            businesses__isnull=False
        ).distinct()
    
    def lastmod(self, obj):
        # Get the most recent business update in this category
        latest_business = obj.businesses.filter(
            is_active=True,
            is_approved=True
        ).order_by('-updated_at').first()
        
        if latest_business and hasattr(latest_business, 'updated_at'):
            return latest_business.updated_at
        return timezone.now()
    
    def location(self, obj):
        return reverse('category_detail', kwargs={'pk': obj.pk, 'slug': obj.slug})


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'monthly'
    protocol = 'https'
    
    def items(self):
        # List of static page names (URL names)
        return [
            'home',
            'about',
            'contact',
            'business_list',
            'category_list',
            'add_business',
            'privacy_policy',
            'terms_of_service',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        # Static pages don't change often
        return timezone.now().replace(day=1)  # First day of current month


class LocationSitemap(Sitemap):
    """Sitemap for location-based pages (if you have location filtering)"""
    changefreq = "weekly"
    priority = 0.7
    protocol = 'https'
    
    def items(self):
        # Get unique cities/locations from businesses
        return Business.objects.filter(
            is_active=True,
            is_approved=True,
            city__isnull=False
        ).values_list('city', flat=True).distinct()
    
    def location(self, item):
        # Assuming you have a location-based view
        return reverse('businesses_by_location', kwargs={'city': item.lower().replace(' ', '-')})
    
    def lastmod(self, obj):
        # Get the latest business update for this city
        latest = Business.objects.filter(
            city=obj,
            is_active=True,
            is_approved=True
        ).order_by('-updated_at').first()
        
        return latest.updated_at if latest else timezone.now()


class FeaturedBusinessSitemap(Sitemap):
    """Separate sitemap for featured businesses with higher priority"""
    changefreq = "daily"
    priority = 1.0
    protocol = 'https'
    
    def items(self):
        return Business.objects.filter(
            is_active=True,
            is_approved=True,
            is_featured=True
        )
    
    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return reverse('business_detail', kwargs={'pk': obj.pk, 'slug': obj.slug})


# If you have blog posts or articles
class BlogSitemap(Sitemap):
    """Sitemap for blog posts/articles"""
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        # Assuming you have a Blog/Article model
        try:
            from .models import Article
            return Article.objects.filter(is_published=True)
        except ImportError:
            return []
    
    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return reverse('article_detail', kwargs={'pk': obj.pk, 'slug': obj.slug})