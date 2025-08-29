# business_directory/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.sitemaps.views import sitemap
from . import views as project_views

# Simple fallback home view
def home_view(request):
    """Home page fallback"""
    context = {
        'total_businesses': 0,
        'total_categories': 0,
        'total_reviews': 0,
        'featured_businesses': [],
        'popular_categories': [],
    }
    return render(request, 'home.html', context)

# Health check
def health_check(request):
    return HttpResponse("OK", content_type='text/plain')

# Custom error handlers
def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)

def custom_500(request):
    return render(request, '500.html', {}, status=500)

# Sitemaps disabled for now
HAS_SITEMAPS = False
sitemaps = {}

# Main URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('robots.txt', project_views.robots_txt, name='robots_txt'),
    path('health/', health_check, name='health_check'),
    path('about/', project_views.AboutView.as_view(), name='about'),
    path('contact/', project_views.ContactView.as_view(), name='contact'),
    path('privacy/', project_views.PrivacyView.as_view(), name='privacy'),
    path('terms/', project_views.TermsView.as_view(), name='terms'),
    path('help/', project_views.HelpView.as_view(), name='help'),
    path('pricing/', project_views.PricingView.as_view(), name='pricing'),
    path('search/global/', project_views.global_search, name='global_search'),
    path('ajax/location-autocomplete/', project_views.location_autocomplete, name='location_autocomplete'),
]

# Include app URLs - Simplified format that matches INSTALLED_APPS
urlpatterns.append(path('businesses/', include('apps.businesses.urls')))
urlpatterns.append(path('categories/', include('apps.categories.urls')))
urlpatterns.append(path('reviews/', include('apps.reviews.urls')))
urlpatterns.append(path('accounts/', include('apps.accounts.urls')))
urlpatterns.append(path('api/', include('apps.api.urls')))

# Sitemap
if HAS_SITEMAPS:
    urlpatterns.append(path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'))

# Error handlers
handler404 = custom_404
handler500 = custom_500

# Development static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar (optional)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass

# Admin site customization
admin.site.site_header = 'LocalBiz Administration'
admin.site.site_title = 'LocalBiz Admin'
admin.site.index_title = 'Welcome to LocalBiz Administration'