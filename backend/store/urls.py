from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # Product Browsing Views
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('new-releases/', views.NewReleasesView.as_view(), name='new_releases'),
    
    # Search Views
    path('search/', views.SearchView.as_view(), name='search'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    
    # Review Views
    path('review/create/', views.CreateReviewView.as_view(), name='create_review'),
    path('review/<int:review_id>/helpful/', views.ReviewHelpfulView.as_view(), name='review_helpful'),
]