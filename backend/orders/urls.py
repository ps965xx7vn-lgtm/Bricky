from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    # Cart URLs
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/', views.UpdateCartItemView.as_view(), name='update_cart'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear_cart'),
    
    # Checkout URLs
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/place/', views.PlaceOrderView.as_view(), name='place_order'),
    path('order/<uuid:order_uuid>/confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('set-shipping/', views.SetShippingView.as_view(), name='set_shipping'),
    
    # Order List URL
    path('orders/', views.OrderListView.as_view(), name='order_list'),
]