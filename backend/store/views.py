"""Views for store app.

Handles product catalog, categories, search, product details, and reviews.
"""
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from store.models import Product, Category, Review
from store.forms import ReviewForm


# ===== Main Catalog Views =====

class IndexView(ListView):
    """Display main product catalog with filtering and sorting.
    
    Features:
    - Category filtering
    - Price range filtering
    - Search by name/description
    - Multiple sorting options
    """
    model = Product
    template_name = 'core/index.html'
    context_object_name = 'object_list'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Price filters
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


class ShopView(ListView):
    """Display shop page with advanced filtering.
    
    Features:
    - Multiple category selection
    - Price range filtering
    - Stock availability filtering
    - Multiple sorting options (newest, price, name, popular)
    """
    model = Product
    template_name = 'store/shop/shop.html'
    context_object_name = 'object_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Category filter
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category__slug__in=categories)
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Availability filter
        availability = self.request.GET.get('availability')
        if availability == 'in_stock':
            queryset = queryset.filter(stock__gt=0)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        sort_mapping = {
            'newest': '-created_at',
            'price-low': 'price',
            'price-high': '-price',
            'name': 'name',
            'popular': '-stock'
        }
        queryset = queryset.order_by(sort_mapping.get(sort, sort))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_categories'] = self.request.GET.getlist('category')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['products_count'] = self.get_queryset().count()
        
        return context


class CategoryView(ShopView):
    """Display products within a specific category.
    
    Inherits filtering and sorting from ShopView.
    Adds category-specific information and related categories.
    """
    template_name = 'store/product/category.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('slug')
        return queryset.filter(category__slug=category_slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        context['category'] = get_object_or_404(Category, slug=category_slug)
        context['other_categories'] = Category.objects.exclude(slug=category_slug)[:6]
        
        all_products = Product.objects.filter(category__slug=category_slug, is_active=True)
        if all_products.exists():
            context['min_price_stat'] = all_products.order_by('price').first().price
        
        return context


class NewReleasesView(ShopView):
    """Display new releases page.
    
    Shows products categorized as:
    - New products
    - Old/discounted products
    - Coming soon products
    
    Supports status filtering and sorting.
    """
    template_name = 'store/shop/new_releases.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by new/old/coming soon status
        queryset = queryset.filter(status__in=['N', 'O', 'C'])
        
        # Apply status filter if provided
        status = self.request.GET.get('status', '')
        status_map = {'new': 'N', 'old': 'O', 'coming_soon': 'C'}
        if status in status_map:
            queryset = queryset.filter(status=status_map[status])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        sort = self.request.GET.get('sort', '-created_at')
        sort_mapping = {
            'newest': '-created_at',
            'price-low': 'price',
            'price-high': '-price',
        }
        order_by = sort_mapping.get(sort, sort)
        
        # Get products by status
        context['new_products'] = Product.objects.filter(
            is_active=True, status='N'
        ).select_related('category').order_by(order_by)
        
        context['old_products'] = Product.objects.filter(
            is_active=True, status='O'
        ).select_related('category').order_by(order_by)
        
        context['coming_soon_products'] = Product.objects.filter(
            is_active=True, status='C'
        ).select_related('category').order_by(order_by)
        
        context['status_filter'] = self.request.GET.get('status', '')
        
        return context


# ===== Product Detail View =====

class ProductDetailView(DetailView):
    """Display product details with reviews.
    
    Shows:
    - Product information
    - Approved reviews
    - Average rating
    - Review form (for authenticated users)
    """
    template_name = 'store/product/product_detail.html'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get approved reviews
        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['reviews'] = reviews
        context['review_count'] = reviews.count()
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = avg_rating or 0
        
        # Check if user has reviewed
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = product.reviews.filter(
                author=self.request.user
            ).exists()
            context['review_form'] = ReviewForm()
        
        return context


# ===== Search Views =====

class SearchView(ListView):
    """Comprehensive product search.
    
    Searches in:
    - Product names
    - Product descriptions
    - Category names
    
    Minimum query length: 2 characters
    """
    model = Product
    template_name = 'store/shop/search.html'
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Product.objects.none()
        
        return Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__title__icontains=query),
            is_active=True
        ).select_related('category').distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        context['search_query'] = query
        context['query_length'] = len(query)
        context['search_performed'] = len(query) >= 2
        
        if context['search_performed']:
            context['total_results'] = self.get_queryset().count()
            context['categories'] = Category.objects.filter(title__icontains=query)
        
        return context


def search_api(request):
    """Unified API for search and autocomplete.
    
    Query parameters:
    - q: search query
    - type: 'full' (default) or 'autocomplete'
    
    Returns JSON with products and categories.
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'full')  # 'full' or 'autocomplete'
    
    if not query or len(query) < 1:
        return JsonResponse({
            'suggestions': [] if search_type == 'autocomplete' else {},
            'products': [],
            'categories': []
        })
    
    if search_type == 'autocomplete':
        # Quick autocomplete suggestions
        products = Product.objects.filter(
            name__icontains=query, is_active=True
        ).values_list('name', flat=True).distinct()[:10]
        
        categories = Category.objects.filter(
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:5]
        
        return JsonResponse({
            'products': list(products),
            'categories': list(categories),
        })
    
    # Full search results
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).values('id', 'name', 'slug', 'price')[:5]
    
    categories = Category.objects.filter(
        title__icontains=query
    ).values('id', 'title', 'slug')[:3]
    
    return JsonResponse({
        'products': list(products),
        'categories': list(categories),
    })


# ===== Review Views =====

class CreateReviewView(LoginRequiredMixin, View):
    """Create product review.
    
    AJAX endpoint for submitting product reviews.
    Validates user hasn't already reviewed the product.
    Returns JSON with success status and review data.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id, is_active=True)

            # Check if user already reviewed
            if Review.objects.filter(product=product, author=request.user).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'You have already reviewed this product.'
                }, status=400)

            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.author = request.user
                review.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Review submitted successfully!',
                    'review': {
                        'author': review.author.username,
                        'rating': review.rating,
                        'title': review.title,
                        'content': review.content,
                        'created_at': review.created_at.strftime('%B %d, %Y')
                    }
                })
            
            return JsonResponse({
                'success': False,
                'message': 'Please fix the errors.',
                'errors': form.errors
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)


class ReviewHelpfulView(LoginRequiredMixin, View):
    """Mark review as helpful or unhelpful.
    
    AJAX endpoint for voting on review helpfulness.
    Returns JSON with updated helpful/unhelpful counts.
    """
    
    def post(self, request, review_id):
        try:
            review = get_object_or_404(Review, id=review_id)
            action = request.POST.get('action')

            if action == 'helpful':
                review.helpful_count += 1
            elif action == 'unhelpful':
                review.unhelpful_count += 1
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action.'
                }, status=400)

            review.save()

            return JsonResponse({
                'success': True,
                'helpful_count': review.helpful_count,
                'unhelpful_count': review.unhelpful_count
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
