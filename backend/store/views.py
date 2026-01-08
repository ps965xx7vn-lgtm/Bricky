from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from store.models import Product, Category
from core.models import Review
from core.forms import ReviewForm


# ============ CATEGORY VIEW ============

class CategoryView(ListView):
    """
    Category detail page showing all products for a specific category with filtering
    """
    model = Product
    template_name = 'store/product/category.html'
    context_object_name = 'object_list'
    paginate_by = 20

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        queryset = Product.objects.filter(
            category__slug=category_slug, 
            is_active=True
        ).select_related('category')
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Stock availability filter
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        category = Category.objects.get(slug=category_slug)
        
        # Get filter values
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        in_stock = self.request.GET.get('in_stock', '')
        sort = self.request.GET.get('sort', '-created_at')
        
        # Get products for stats
        all_products = Product.objects.filter(category__slug=category_slug, is_active=True)
        
        context['category'] = category
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['in_stock'] = in_stock
        context['sort'] = sort
        context['products_count'] = all_products.count()
        context['other_categories'] = Category.objects.exclude(slug=category_slug)[:6]
        
        # Get min price for stats
        if all_products.exists():
            context['min_price_stat'] = all_products.order_by('price').first().price
        else:
            context['min_price_stat'] = 0
        
        return context


class ShopView(ListView):
    """
    Dedicated shop page with advanced filtering and sorting
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
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'price-low':
            queryset = queryset.order_by('price')
        elif sort == 'price-high':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        elif sort == 'popular':
            queryset = queryset.order_by('-stock')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_categories'] = self.request.GET.getlist('category')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        
        return context


class ProductDetailView(DetailView):
    """
    View for displaying a single product's details with reviews
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
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            context['average_rating'] = total_rating / reviews.count()
        else:
            context['average_rating'] = 0
        
        # Check if user has already reviewed this product
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = product.reviews.filter(author=self.request.user).exists()
            context['review_form'] = ReviewForm()
        else:
            context['user_has_reviewed'] = False
            context['review_form'] = None
        
        return context


class NewReleasesView(TemplateView):
    """
    View for displaying the New Releases page with old and coming soon products
    """
    template_name = 'store/shop/new_releases.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get status filter from query params
        status = self.request.GET.get('status', '')
        
        # Get sorting from query params
        sort = self.request.GET.get('sort', '-created_at')
        
        # Base queryset for active products with NEW, OLD or COMING_SOON status
        queryset = Product.objects.filter(
            is_active=True,
            status__in=['N', 'O', 'C']  # New, Old and Coming Soon products
        ).select_related('category')
        
        # Apply status filter if provided
        if status == 'new':
            queryset = queryset.filter(status='N')
        elif status == 'old':
            queryset = queryset.filter(status='O')
        elif status == 'coming_soon':
            queryset = queryset.filter(status='C')
        
        # Apply sorting
        queryset = queryset.order_by(sort)
        
        # Separate products by status
        new_products = Product.objects.filter(
            is_active=True,
            status='N'
        ).select_related('category').order_by(sort)
        
        old_products = Product.objects.filter(
            is_active=True,
            status='O'
        ).select_related('category').order_by(sort)
        
        coming_soon_products = Product.objects.filter(
            is_active=True,
            status='C'
        ).select_related('category').order_by(sort)
        
        context['products'] = queryset
        context['new_products'] = new_products
        context['old_products'] = old_products
        context['coming_soon_products'] = coming_soon_products
        context['status_filter'] = status
        context['sort'] = sort
        context['categories'] = Category.objects.all()
        
        return context


class SearchView(ListView):
    """
    Comprehensive search view for products and categories
    """
    model = Product
    template_name = 'store/shop/search.html'
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


# ============ SEARCH API VIEWS ============

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


# ============ REVIEW VIEWS ============

class CreateReviewView(LoginRequiredMixin, View):
    """
    View for creating a product review
    """
    model = Review
    form_class = ReviewForm
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """Handle review submission via AJAX"""
        try:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id, is_active=True)

            # Check if user already reviewed this product
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
                    'message': 'Review submitted successfully! It will appear after moderation.',
                    'review': {
                        'author': review.author.username,
                        'rating': review.rating,
                        'title': review.title,
                        'content': review.content,
                        'created_at': review.created_at.strftime('%B %d, %Y')
                    }
                })
            else:
                errors = form.errors
                return JsonResponse({
                    'success': False,
                    'message': 'Please fix the errors below.',
                    'errors': errors
                }, status=400)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)


class ReviewHelpfulView(LoginRequiredMixin, View):
    """
    AJAX view to mark review as helpful or unhelpful
    """
    def post(self, request, review_id):
        """Handle helpful/unhelpful marking"""
        try:
            review = get_object_or_404(Review, id=review_id)
            action = request.POST.get('action')  # 'helpful' or 'unhelpful'

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
                'message': f'An error occurred: {str(e)}'
            }, status=500)
