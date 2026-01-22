"""URL configuration for store app.

Handles product catalog, search, categories, and reviews.
"""
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # ===== Main Pages =====
    path('', views.IndexView.as_view(), name='index'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('new-releases/', views.NewReleasesView.as_view(), name='new_releases'),
    
    # ===== Product Views =====
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # ===== Search =====
    path('search/', views.SearchView.as_view(), name='search'),
    path('api/search/', views.search_api, name='search_api'),
    
    # ===== Reviews =====
    path('review/create/', views.CreateReviewView.as_view(), name='create_review'),
    path('review/<int:review_id>/helpful/', views.ReviewHelpfulView.as_view(), name='review_helpful'),
]