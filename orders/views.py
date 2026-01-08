from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal

from store.models import Cart, CartItem, Product
from orders.models import Order, Customer, OrderElement


# ============ CART VIEWS ============

class CartView(LoginRequiredMixin, TemplateView):
    """
    Display user's shopping cart with all items
    """
    template_name = 'orders/cart/cart.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        
        context['cart'] = cart
        context['cart_items'] = cart.items.all().select_related('product')
        context['total_price'] = cart.get_total_price()
        context['total_items'] = cart.get_total_items()
        
        # Get shipping cost from session or use default
        shipping_cost_str = self.request.session.get('shipping_cost', '10.00')
        try:
            context['shipping_cost'] = Decimal(shipping_cost_str)
        except:
            context['shipping_cost'] = Decimal('10.00')
        
        context['grand_total'] = context['total_price'] + context['shipping_cost']
        
        return context


class AddToCartView(View):
    """
    Add a product to the user's cart (AJAX endpoint)
    Requires authentication
    """

    def post(self, request, *args, **kwargs):
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Please log in to add items to cart',
                    'requires_login': True
                }, status=401)
            
            product_id = request.POST.get('product_id')
            
            # Validate product_id
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Product ID is required'
                }, status=400)
            
            # Get quantity with proper error handling
            try:
                quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid quantity value'
                }, status=400)
            
            # Validate quantity
            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Quantity must be at least 1'
                }, status=400)
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Product not found'
                }, status=404)
            
            # Validate stock
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock'
                }, status=400)
            
            if request.user.is_authenticated:
                # For authenticated users, use database cart
                cart, created = Cart.objects.get_or_create(user=request.user)
                
                # Add or update cart item
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    # Item already in cart, update quantity
                    cart_item.quantity += quantity
                    cart_item.save()
                except CartItem.DoesNotExist:
                    # Create new cart item
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        price=product.price,
                        quantity=quantity
                    )
                
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} added to cart',
                    'cart_count': cart.get_total_items(),
                    'cart_total': str(cart.get_total_price()),
                    'requires_login': False
                })
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in AddToCartView: {str(e)}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while adding to cart'
            }, status=500)


class RemoveFromCartView(LoginRequiredMixin, View):
    """
    Remove an item from the cart
    """
    login_url = 'users:login'

    def post(self, request, *args, **kwargs):
        try:
            # Get cart_item_id from POST data
            cart_item_id = request.POST.get('cart_item_id')
            
            if not cart_item_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Cart item ID is required'
                }, status=400)
            
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            cart = cart_item.cart
            product_name = cart_item.product.name
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart',
                'cart_count': cart.get_total_items(),
                'cart_total': str(cart.get_total_price())
            })
        
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Item not found in cart'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)


class UpdateCartItemView(LoginRequiredMixin, View):
    """
    Update quantity of an item in the cart
    """
    login_url = 'users:login'

    def post(self, request, *args, **kwargs):
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            
            # Validate quantity
            if quantity < 1:
                cart_item.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Item removed from cart'
                })
            
            # Validate stock
            if cart_item.product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {cart_item.product.stock} items available in stock'
                }, status=400)
            
            cart_item.quantity = quantity
            cart_item.save()
            cart = cart_item.cart
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'item_total': str(cart_item.get_total_price()),
                'cart_count': cart.get_total_items(),
                'cart_total': str(cart.get_total_price())
            })
        
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Item not found'
            }, status=404)


class ClearCartView(LoginRequiredMixin, View):
    """
    Clear all items from the cart
    """
    login_url = 'users:login'

    def post(self, request, *args, **kwargs):
        try:
            # Get or create cart for user
            cart = Cart.objects.get(user=request.user)
            
            # Delete all items in cart
            CartItem.objects.filter(cart=cart).delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart cleared successfully',
                'cart_count': 0,
                'cart_total': '0.00'
            })
        
        except Cart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cart not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error clearing cart: {str(e)}'
            }, status=500)


# ============ CHECKOUT VIEWS ============

class CheckoutView(LoginRequiredMixin, TemplateView):
    """
    Checkout page with shipping and payment information
    """
    template_name = 'orders/cart/checkout.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cart = Cart.objects.get(user=self.request.user)
            context['cart'] = cart
            context['cart_items'] = cart.items.all().select_related('product')
            context['total_price'] = cart.get_total_price()
            
            # Get shipping cost from session or use default
            shipping_cost_str = self.request.session.get('shipping_cost', '10.00')
            try:
                context['shipping_cost'] = Decimal(shipping_cost_str)
            except:
                context['shipping_cost'] = Decimal('10.00')
            
            context['grand_total'] = context['total_price'] + context['shipping_cost']
            
            # Get or create customer
            customer, created = Customer.objects.get_or_create(user=self.request.user)
            context['customer'] = customer
            
        except Cart.DoesNotExist:
            context['empty_cart'] = True
        
        return context


class PlaceOrderView(LoginRequiredMixin, View):
    """
    Process the checkout and create an order
    """
    login_url = 'users:login'

    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
            
            if not cart.items.exists():
                messages.error(request, 'Your cart is empty')
                return redirect('orders:cart')
            
            # Get or create customer
            customer, created = Customer.objects.get_or_create(user=request.user)
            
            # Update customer info from form
            customer.phone = request.POST.get('phone', customer.phone)
            customer.address = request.POST.get('address', customer.address)
            customer.save()
            
            # Create order with shipping cost from session
            shipping_cost_str = request.session.get('shipping_cost', '10.00')
            try:
                shipping_cost = Decimal(shipping_cost_str)
            except:
                shipping_cost = Decimal('10.00')
            
            subtotal = cart.get_total_price()
            total = subtotal + shipping_cost
            
            order = Order.objects.create(
                customer=customer,
                total_price=total,
                status='N',
                address=request.POST.get('address', customer.address) or 'Not provided',
                is_draft=False
            )
            
            # Add items to order
            for cart_item in cart.items.all():
                OrderElement.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('orders:order_confirmation', order_uuid=order.uuid)
        
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found')
            return redirect('orders:cart')
        except Exception as e:
            messages.error(request, f'Error placing order: {str(e)}')
            return redirect('orders:checkout')


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """
    Display order confirmation page
    """
    model = Order
    template_name = 'orders/cart/order_confirmation.html'
    context_object_name = 'order'
    login_url = 'users:login'
    pk_url_kwarg = 'order_uuid'

    def get_queryset(self):
        # Only show orders for the current user
        return Order.objects.filter(customer__user=self.request.user)
    
    def get_object(self, queryset=None):
        """Override to use uuid instead of pk"""
        if queryset is None:
            queryset = self.get_queryset()
        order_uuid = self.kwargs.get('order_uuid')
        return queryset.get(uuid=order_uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['order_items'] = order.order_items.all()
        context['shipping_cost'] = Decimal('10.00')
        
        return context


class SetShippingView(LoginRequiredMixin, View):
    """
    Save selected shipping method and cost to session
    """
    login_url = 'users:login'
    
    def post(self, request, *args, **kwargs):
        try:
            shipping_method = request.POST.get('shipping_method')
            shipping_cost = request.POST.get('shipping_cost')
            
            # Store in session
            request.session['shipping_method'] = shipping_method
            request.session['shipping_cost'] = shipping_cost
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'Shipping method set to {shipping_method}'
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in SetShippingView: {str(e)}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'Error setting shipping method'
            }, status=500)

# ============ ORDER LIST VIEW ============

class OrderListView(LoginRequiredMixin, TemplateView):
    """
    Display all orders for the current user
    """
    template_name = 'orders/order_list.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            customer = self.request.user.customer
            orders = Order.objects.filter(customer=customer, is_draft=False).order_by('-registered_at')
            context['orders'] = orders
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not fetch orders for user {self.request.user.username}: {str(e)}")
            context['orders'] = []
        
        return context