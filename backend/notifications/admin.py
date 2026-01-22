"""Admin interface for notifications app.

Handles newsletter subscription management in Django admin.
"""
from django.contrib import admin
from django.utils.html import format_html

from notifications.models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for NewsletterSubscription model."""
    
    list_display = ('email', 'status_badge', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('status', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('id', 'subscribed_at', 'unsubscribed_at')
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('email', 'status')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        status_colors = {
            'active': '#28a745',
            'unsubscribed': '#6c757d',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    ordering = ('-subscribed_at',)
