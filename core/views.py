from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import json

from users.models import CustomUser
from orders.models import Order, Customer
from store.models import Product, Category


class IndexView(ListView):
    
    """
    LEGO store main page showing all products with filters and categories
    """
    model = Product
    template_name = 'core/index.html'
    context_object_name = 'object_list'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort'] = self.request.GET.get('sort', '-created_at')
        
        # Price range for filter
        products = Product.objects.filter(is_active=True)
        if products.exists():
            context['price_max'] = products.order_by('-price').first().price
            context['price_min'] = products.order_by('price').first().price
        
        return context


class ProductDetailView(DetailView):
    """
    View for displaying a single product's details
    """
    model = Product
    template_name = 'core/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class PrivacyPolicyView(TemplateView):
    """
    View for displaying the Privacy Policy page
    """
    template_name = 'core/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    """
    View for displaying the Terms of Service page
    """
    template_name = 'core/terms_of_service.html'


class CookieSettingsView(TemplateView):
    """
    View for displaying the Cookie Settings page
    """
    template_name = 'core/cookie_settings.html'


class AboutView(TemplateView):
    """
    View for displaying the About page
    """
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """
    View for displaying the Contact page
    """
    template_name = 'core/contact.html'


class NewReleasesView(TemplateView):
    """
    View for displaying the New Releases page
    """
    template_name = 'core/new_releases.html'


class SearchView(ListView):
    """
    Comprehensive search view for products and categories
    """
    model = Product
    template_name = 'core/search.html'
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Product.objects.none()
        
        # Search in products
        queryset = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__title__icontains=query),
            is_active=True
        ).select_related('category').distinct()
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        context['search_query'] = query
        context['query_length'] = len(query)
        
        # Get search statistics
        if query and len(query) >= 2:
            products = self.get_queryset()
            categories = Category.objects.filter(title__icontains=query)
            
            context['total_results'] = products.count()
            context['categories'] = categories
            context['search_performed'] = True
        else:
            context['search_performed'] = False
        
        return context


def search_api(request):
    """
    API endpoint for instant search suggestions
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search products
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).values('id', 'name', 'slug', 'price')[:5]
    
    # Search categories
    categories = Category.objects.filter(
        title__icontains=query
    ).values('id', 'title', 'slug')[:3]
    
    results = {
        'products': list(products),
        'categories': list(categories),
    }
    
    return JsonResponse(results)


def search_autocomplete(request):
    """
    Autocomplete suggestions for search bar
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 1:
        return JsonResponse({'suggestions': []})
    
    # Get product names
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).values_list('name', flat=True).distinct()[:10]
    
    # Get category names
    categories = Category.objects.filter(
        title__icontains=query
    ).values_list('title', flat=True).distinct()[:5]
    
    suggestions = {
        'products': list(products),
        'categories': list(categories),
    }
    
    return JsonResponse(suggestions)
