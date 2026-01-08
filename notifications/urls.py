from django.urls import path

from notifications import views

app_name = "notifications"

urlpatterns = [
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/subscribe-ajax/', views.NewsletterSubscribeAjaxView.as_view(), name='newsletter_subscribe_ajax'),
    path('newsletter/unsubscribe-ajax/', views.NewsletterUnsubscribeAjaxView.as_view(), name='newsletter_unsubscribe_ajax'),
    path('newsletter/success/', views.NewsletterSuccessView.as_view(), name='newsletter_success'),
]