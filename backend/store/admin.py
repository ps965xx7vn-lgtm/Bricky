from django.contrib import admin
from django.utils.html import format_html
from store.models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'slug']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', "status" ,'category', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name',"status" ,'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('picture',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model."""
    
    list_display = (
        'product_name',
        'author_name',
        'rating_stars',
        'approval_badge',
        'created_at'
    )
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = (
        'product__name',
        'author__username',
        'title',
        'content'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'helpful_count',
        'unhelpful_count'
    )
    
    fieldsets = (
        ('Product & Author', {
            'fields': ('product', 'author')
        }),
        ('Review Content', {
            'fields': ('title', 'content', 'rating')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Feedback', {
            'fields': ('helpful_count', 'unhelpful_count'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_name(self, obj):
        """Display product name."""
        return obj.product.name
    product_name.short_description = 'Product'
    
    def author_name(self, obj):
        """Display author username."""
        return obj.author.username
    author_name.short_description = 'Author'
    
    def rating_stars(self, obj):
        """Display rating as stars."""
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return f"{stars} ({obj.rating}/5)"
    rating_stars.short_description = 'Rating'
    
    def approval_badge(self, obj):
        """Display approval status as colored badge."""
        color = '#28a745' if obj.is_approved else '#dc3545'
        status = 'Approved' if obj.is_approved else 'Pending'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            status
        )
    approval_badge.short_description = 'Status'
    
    ordering = ('-created_at',)

