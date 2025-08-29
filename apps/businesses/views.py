# apps/businesses/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Business
from apps.categories.models import Category  # Fixed import

# ------------------------
# AJAX Search View
# ------------------------
def business_search_ajax(request):
    query = request.GET.get('q', '')
    businesses = []
    
    if query and len(query) > 2:  # Only search if query is longer than 2 chars
        results = Business.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query)
        ).select_related('category')[:10]
        
        businesses = [{
            'name': business.name,
            'slug': business.slug,
            'city': business.city,
            'state': business.state,
            'category': business.category.name if business.category else '',
            'url': business.get_absolute_url(),
        } for business in results]
    
    return JsonResponse({'businesses': businesses})

# ------------------------
# Home View
# ------------------------
class HomeView(TemplateView):
    template_name = "businesses/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured businesses for homepage
        context['featured_businesses'] = Business.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category')[:6]
        context['categories'] = Category.objects.all()[:8]
        return context

# ------------------------
# Business List View
# ------------------------
class BusinessListView(ListView):
    model = Business
    template_name = "businesses/business_list.html"
    context_object_name = "businesses"
    paginate_by = 12  # optional pagination
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').filter(is_active=True)
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by search query (template uses 'search', not 'q')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            ).distinct()
        
        # Filter by location
        location_query = self.request.GET.get('location')
        if location_query:
            queryset = queryset.filter(
                Q(city__icontains=location_query) |
                Q(state__icontains=location_query) |
                Q(address__icontains=location_query)
            ).distinct()
        
        # Sort results
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'rating':
            # This would need annotation for proper sorting by rating
            queryset = queryset.order_by('-is_featured', '-created_at')  # Fallback for now
        elif sort_by == 'reviews':
            # This would need annotation for proper sorting by review count
            queryset = queryset.order_by('-is_featured', '-created_at')  # Fallback for now
        else:  # default: -created_at
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', None)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_location'] = self.request.GET.get('location', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context

# ------------------------
# Business Detail View
# ------------------------
class BusinessDetailView(DetailView):
    model = Business
    template_name = "businesses/business_detail.html"
    context_object_name = "business"
    slug_field = 'slug'  # Use slug instead of pk
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Business.objects.filter(is_active=True).select_related('category', 'owner')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment views count
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj

# ------------------------
# Business Create View
# ------------------------
class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    template_name = "businesses/business_form.html"
    fields = ['name', 'description', 'address', 'city', 'state', 'zip_code', 
              'email', 'phone', 'website', 'logo', 'featured_image', 'category']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

# ------------------------
# Business Update View
# ------------------------
class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    template_name = "businesses/business_form.html"
    fields = ['name', 'description', 'address', 'city', 'state', 'zip_code', 
              'email', 'phone', 'website', 'logo', 'featured_image', 'category']
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        # Users can only edit their own businesses
        return Business.objects.filter(owner=self.request.user)

# ------------------------
# Business Delete View
# ------------------------
class BusinessDeleteView(LoginRequiredMixin, DeleteView):
    model = Business
    template_name = "businesses/business_confirm_delete.html"
    success_url = reverse_lazy('businesses:list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        # Users can only delete their own businesses
        return Business.objects.filter(owner=self.request.user)

# ------------------------
# Optional: Global search view
# ------------------------
def global_search(request):
    query = request.GET.get('search', '')  # Changed from 'q' to 'search'
    location = request.GET.get('location', '')
    
    businesses = Business.objects.filter(is_active=True)
    
    if query:
        businesses = businesses.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    if location:
        businesses = businesses.filter(
            Q(city__icontains=location) |
            Q(state__icontains=location) |
            Q(address__icontains=location)
        ).distinct()
    
    categories = Category.objects.all()
    
    context = {
        "businesses": businesses,
        "categories": categories,
        "current_search": query,
        "current_location": location,
        "current_sort": request.GET.get('sort', '-created_at'),
    }
    return render(request, "businesses/business_list.html", context)