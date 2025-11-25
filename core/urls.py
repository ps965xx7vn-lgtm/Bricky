from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('new-releases/', views.NewReleasesView.as_view(), name='new_releases'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('cookie-settings/', views.CookieSettingsView.as_view(), name='cookie_settings'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
]