# business_directory/views.py
"""
Project-level views for business_directory.
These include global functionality, error handlers, and utility views.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
import json
import logging

from apps.businesses.models import Business
from apps.categories.models import Category
from apps.reviews.models import Review

# Setup logging
logger = logging.getLogger(__name__)


# Global Context Processor Data
def get_global_context():
    """Get global context data used across the site"""
    try:
        return {
            'total_businesses': Business.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_reviews': Review.objects.filter(is_approved=True).count(),
            'featured_categories': Category.objects.filter(is_active=True)[:6],
        }
    except Exception as e:
        logger.error(f"Error getting global context: {e}")
        return {}


# Static Page Views
class AboutView(TemplateView):
    """About Us page"""
    template_name = 'pages/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'About LocalBiz',
            'stats': get_global_context(),
        })
        return context


class ContactView(TemplateView):
    """Contact Us page"""
    template_name = 'pages/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if all([name, email, subject, message]):
            try:
                # Send email to admin
                full_message = f"""
                Contact Form Submission
                
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                """
                
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(request, 'Thank you for your message. We\'ll get back to you soon!')
                return redirect('contact')
                
            except Exception as e:
                logger.error(f"Contact form email error: {e}")
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        
        return self.get(request, *args, **kwargs)


class PrivacyView(TemplateView):
    """Privacy Policy page"""
    template_name = 'pages/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Privacy Policy'
        context['last_updated'] = '2024-01-01'  # Update as needed
        return context


class TermsView(TemplateView):
    """Terms of Service page"""
    template_name = 'pages/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Terms of Service'
        context['last_updated'] = '2024-01-01'  # Update as needed
        return context


class HelpView(TemplateView):
    """Help Center page"""
    template_name = 'pages/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Help Center',
            'faq_items': self.get_faq_items(),
        })
        return context
    
    def get_faq_items(self):
        """Return FAQ items"""
        return [
            {
                'question': 'How do I add my business to the directory?',
                'answer': 'Sign up for an account and click "Add Your Business" in the navigation menu. Fill out the form with your business details and submit for review.'
            },
            {
                'question': 'How long does it take for my business to be approved?',
                'answer': 'Business listings are typically reviewed and approved within 24-48 hours of submission.'
            },
            {
                'question': 'Can I edit my business information after it\'s published?',
                'answer': 'Yes, you can edit your business information at any time from your dashboard. Changes may require re-approval.'
            },
            {
                'question': 'How do I respond to reviews?',
                'answer': 'Currently, business owners can contact reviewers directly or address concerns by updating their business information.'
            },
            {
                'question': 'Is there a cost to list my business?',
                'answer': 'Basic business listings are free. We also offer premium features for enhanced visibility.'
            },
        ]


class PricingView(TemplateView):
    """Pricing page for business features"""
    template_name = 'pages/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Pricing Plans',
            'plans': self.get_pricing_plans(),
        })
        return context
    
    def get_pricing_plans(self):
        """Return pricing plan information"""
        return [
            {
                'name': 'Basic',
                'price': 'Free',
                'description': 'Perfect for getting started',
                'features': [
                    'Basic business listing',
                    'Contact information display',
                    'Customer reviews',
                    'Photo upload (5 images)',
                    'Basic analytics',
                ],
                'button_text': 'Get Started',
                'button_class': 'btn-outline-primary',
            },
            {
                'name': 'Professional',
                'price': '$19/month',
                'description': 'Best for growing businesses',
                'features': [
                    'Everything in Basic',
                    'Featured listing placement',
                    'Unlimited photo uploads',
                    'Advanced analytics',
                    'Social media integration',
                    'Priority customer support',
                ],
                'button_text': 'Choose Professional',
                'button_class': 'btn-primary',
                'popular': True,
            },
            {
                'name': 'Enterprise',
                'price': '$49/month',
                'description': 'For established businesses',
                'features': [
                    'Everything in Professional',
                    'Multiple locations support',
                    'Custom branding options',
                    'API access',
                    'Dedicated account manager',
                    'Custom integrations',
                ],
                'button_text': 'Contact Sales',
                'button_class': 'btn-outline-primary',
            },
        ]


# AJAX and API Utility Views
@require_http_methods(["GET"])
def global_search(request):
    """Global AJAX search across all content"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = {
        'businesses': [],
        'categories': [],
    }
    
    # Search businesses
    businesses = Business.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    )[:5]
    
    for business in businesses:
        results['businesses'].append({
            'name': business.name,
            'url': business.get_absolute_url(),
            'category': business.category.name,
            'location': f"{business.city}, {business.state}",
            'image': business.featured_image.url if business.featured_image else None,
        })
    
    # Search categories
    categories = Category.objects.filter(
        name__icontains=query,
        is_active=True
    )[:3]
    
    for category in categories:
        results['categories'].append({
            'name': category.name,
            'url': f'/categories/{category.slug}/',
            'business_count': category.business_count(),
        })
    
    return JsonResponse(results)


@require_http_methods(["GET"])
def location_autocomplete(request):
    """Autocomplete for location search"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get unique cities and states from businesses
    locations = Business.objects.filter(
        Q(city__icontains=query) | Q(state__icontains=query),
        is_active=True
    ).values('city', 'state').distinct()[:10]
    
    suggestions = []
    for location in locations:
        suggestions.append(f"{location['city']}, {location['state']}")
    
    return JsonResponse({'suggestions': suggestions})


@require_http_methods(["POST"])
@csrf_exempt
def newsletter_signup(request):
    """Newsletter signup endpoint"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Here you would typically integrate with an email service like Mailchimp
        # For now, we'll just log it
        logger.info(f"Newsletter signup: {email}")
        
        return JsonResponse({
            'success': True, 
            'message': 'Thank you for subscribing to our newsletter!'
        })
    except Exception as e:
        logger.error(f"Newsletter signup error: {e}")
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred. Please try again.'
        })


# Admin and Staff Views
@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics"""
    context = {
        'title': 'LocalBiz Admin Dashboard',
        'stats': {
            'total_businesses': Business.objects.count(),
            'active_businesses': Business.objects.filter(is_active=True).count(),
            'pending_businesses': Business.objects.filter(is_active=False).count(),
            'total_users': Business.objects.values('owner').distinct().count(),
            'total_reviews': Review.objects.count(),
            'pending_reviews': Review.objects.filter(is_approved=False).count(),
            'total_categories': Category.objects.count(),
        },
        'recent_businesses': Business.objects.order_by('-created_at')[:5],
        'recent_reviews': Review.objects.select_related('business', 'user').order_by('-created_at')[:5],
        'top_categories': Category.objects.annotate(
            business_count=Count('business')
        ).order_by('-business_count')[:10],
    }
    return render(request, 'admin/custom_dashboard.html', context)


@staff_member_required
def business_moderation(request):
    """Business moderation interface"""
    status = request.GET.get('status', 'pending')
    
    if status == 'pending':
        businesses = Business.objects.filter(is_active=False)
    else:
        businesses = Business.objects.filter(is_active=True)
    
    paginator = Paginator(businesses, 20)
    page = request.GET.get('page')
    businesses_page = paginator.get_page(page)
    
    context = {
        'businesses': businesses_page,
        'current_status': status,
        'title': f'{status.title()} Businesses',
    }
    
    return render(request, 'admin/business_moderation.html', context)


@staff_member_required
@require_http_methods(["POST"])
def approve_business(request, business_id):
    """Approve a business listing"""
    try:
        business = Business.objects.get(id=business_id)
        business.is_active = True
        business.save()
        
        # Send notification email to business owner
        try:
            send_mail(
                subject='Your Business Listing has been Approved',
                message=f'Congratulations! Your business "{business.name}" has been approved and is now live on LocalBiz.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[business.owner.email],
                fail_silently=True,
            )
        except:
            pass  # Don't fail if email doesn't send
        
        return JsonResponse({'success': True, 'message': 'Business approved successfully'})
    except Business.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Business not found'})
    except Exception as e:
        logger.error(f"Business approval error: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred'})


# Error Handlers
def custom_404_view(request, exception):
    """Custom 404 error page"""
    context = {
        'popular_categories': Category.objects.filter(is_active=True)[:6],
        'featured_businesses': Business.objects.filter(is_featured=True, is_active=True)[:3],
    }
    return render(request, '404.html', context, status=404)


def custom_500_view(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)


def custom_403_view(request, exception):
    """Custom 403 error page"""
    return render(request, '403.html', status=403)


# Health Check and Monitoring
def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Test database connectivity
        business_count = Business.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'business_count': business_count,
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


# Robots.txt
def robots_txt(request):
    """Generate robots.txt dynamically"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/login/",
        "Disallow: /accounts/register/",
        "Disallow: /api/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


# Maintenance Mode
class MaintenanceView(TemplateView):
    """Maintenance mode page"""
    template_name = 'maintenance.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only show maintenance page if maintenance mode is enabled
        if not getattr(settings, 'MAINTENANCE_MODE', False):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)