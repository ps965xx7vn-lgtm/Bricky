"""URL configuration for core app.

Handles content pages, legal documents, and contact functionality.
"""
from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    # ===== Content Pages =====
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # ===== Legal Pages =====
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'), 
]