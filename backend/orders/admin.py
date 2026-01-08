from django.contrib import admin
from django.utils.html import format_html
from orders.models import Customer, Order, OrderElement, Delivery


class OrderElementInline(admin.TabularInline):
    model = OrderElement
    extra = 1
    readonly_fields = ['total_price']
    fields = ['product', 'price', 'quantity', 'total_price']


class DeliveryInline(admin.TabularInline):
    model = Delivery
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at', 'status_badge']
    fields = ['method', 'status_badge', 'tracking_number', 'estimated_delivery_date', 'actual_delivery_date']
    can_delete = False

    def status_badge(self, obj):
        """Display delivery status as colored badge"""
        status_colors = {
            'pending': '#ffc107',
            'in_transit': '#17a2b8',
            'out_for_delivery': '#0dcaf0',
            'delivered': '#28a745',
            'failed': '#dc3545',
            'returned': '#6c757d',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'phone', 'get_orders_count']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['id', 'user']
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_orders_count(self, obj):
        return obj.orders.count()
    get_orders_count.short_description = 'Orders'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'total_price', 'registered_at']
    list_filter = ['status', 'registered_at', 'is_draft']
    search_fields = ['customer__user__username', 'address']
    readonly_fields = ['registered_at', 'id']
    inlines = [OrderElementInline, DeliveryInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'address', 'order_note')
        }),
        ('Status', {
            'fields': ('status', 'is_draft')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Timeline', {
            'fields': ('registered_at', 'called_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Admin interface for Delivery model
    """
    list_display = ['tracking_number', 'order', 'method', 'status_badge', 'estimated_delivery_date', 'actual_delivery_date']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['tracking_number', 'order__id', 'delivery_address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Delivery Information', {
            'fields': ('order', 'tracking_number', 'method', 'status')
        }),
        ('Recipient Information', {
            'fields': ('recipient_name', 'recipient_phone', 'delivery_address', 'delivery_notes')
        }),
        ('Delivery Details', {
            'fields': ('estimated_delivery_date', 'actual_delivery_date', 'signature_required')
        }),
        ('Costs', {
            'fields': ('delivery_cost', 'insurance', 'insurance_cost'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display delivery status as colored badge"""
        status_colors = {
            'pending': '#ffc107',
            'in_transit': '#17a2b8',
            'out_for_delivery': '#0dcaf0',
            'delivered': '#28a745',
            'failed': '#dc3545',
            'returned': '#6c757d',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

@admin.register(OrderElement)
class OrderElementAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['order__customer__user__username', 'product__name']
    readonly_fields = ['id']
