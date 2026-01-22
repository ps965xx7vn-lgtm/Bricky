"""Views for notifications app.

Handles newsletter subscription and unsubscription via both
traditional forms and AJAX requests.
"""
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
import json

from notifications.models import NewsletterSubscription
from notifications.forms import NewsletterSubscriptionForm


# ===== Newsletter Views =====

class NewsletterSubscribeView(View):
    """Handle newsletter subscriptions.
    
    Supports both traditional form submissions and AJAX requests.
    
    GET: Display subscription form
    POST: Process subscription (form or AJAX)
    """
    
    def get(self, request):
        """Display newsletter subscription form."""
        return TemplateView.as_view(
            template_name='notifications/subscribe/newsletter_subscribe.html',
            extra_context={'form': NewsletterSubscriptionForm()}
        )(request)
    
    def post(self, request):
        """Process subscription request (form or AJAX)."""
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Get email from JSON or POST data
            if is_ajax:
                data = json.loads(request.body)
                email = data.get('email', '').strip().lower()
            else:
                email = request.POST.get('email', '').strip().lower()
            
            if not email:
                return self._response(False, 'Email is required.', is_ajax, 400)
            
            # Check if already subscribed
            if NewsletterSubscription.objects.filter(email=email, status='active').exists():
                return self._response(
                    False,
                    'This email is already subscribed.',
                    is_ajax,
                    400
                )
            
            # Create or reactivate subscription
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={'status': 'active'}
            )
            
            if not created and subscription.status == 'unsubscribed':
                subscription.status = 'active'
                subscription.unsubscribed_at = None
                subscription.save()
            
            return self._response(
                True,
                'Thank you for subscribing to our newsletter!',
                is_ajax,
                201 if created else 200
            )
        
        except json.JSONDecodeError:
            return self._response(False, 'Invalid request format.', is_ajax, 400)
        except Exception as e:
            return self._response(
                False,
                'An error occurred. Please try again.',
                is_ajax,
                500
            )
    
    def _response(self, success, message, is_ajax, status=200):
        """Unified response for AJAX and form submissions"""
        if is_ajax:
            return JsonResponse({
                'success': success,
                'message': message
            }, status=status)
        
        # Form submission - redirect with message
        if success:
            messages.success(self.request, message)
            return TemplateView.as_view(
                template_name='notifications/subscribe/newsletter_success.html',
                extra_context={'title': 'Newsletter Subscription Successful'}
            )(self.request)
        else:
            messages.error(self.request, message)
            return TemplateView.as_view(
                template_name='notifications/subscribe/newsletter_subscribe.html',
                extra_context={'form': NewsletterSubscriptionForm()}
            )(self.request)


class NewsletterUnsubscribeView(View):
    """Handle newsletter unsubscriptions.
    
    AJAX-only endpoint for unsubscribing from newsletter.
    Updates subscription status and timestamp.
    """
    
    def post(self, request):
        """Handle unsubscription"""
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email is required.'
                }, status=400)
            
            # Find and unsubscribe
            try:
                subscription = NewsletterSubscription.objects.get(email=email)
                
                if subscription.status == 'active':
                    from django.utils import timezone
                    subscription.status = 'unsubscribed'
                    subscription.unsubscribed_at = timezone.now()
                    subscription.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'You have been unsubscribed.'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'This email is not currently subscribed.'
                    }, status=400)
            
            except NewsletterSubscription.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Email not found in our newsletter list.'
                }, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            }, status=500)
