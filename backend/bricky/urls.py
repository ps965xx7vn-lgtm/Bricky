from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),  # Store app handles main page and products
    path('', include('core.urls')),  # Core app handles legal/contact pages
    path('users/', include('users.urls')),  # User authentication & profiles
    path('orders/', include('orders.urls')),  # Cart & checkout
    path('notifications/', include('notifications.urls')),  # Newsletter
]

# Debug toolbar URLs
if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)