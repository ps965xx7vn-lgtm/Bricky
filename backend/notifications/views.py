from django.views.generic import TemplateView, View, CreateView
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
import json

from core.models import NewsletterSubscription
from core.forms import NewsletterSubscriptionForm
# ============ NEWSLETTER VIEWS ============
class NewsletterSubscribeView(CreateView):
    """
    View for subscribing to the newsletter
    """
    model = NewsletterSubscription
    form_class = NewsletterSubscriptionForm
    template_name = 'notifications/subscribe/newsletter_subscribe.html'
    success_url = reverse_lazy('notifications:newsletter_success')

    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Thank you for subscribing to our newsletter! You\'ll receive updates soon.'
        )
        return response

    def form_invalid(self, form):
        """Handle form errors"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{error}')
        return self.render_to_response(self.get_context_data(form=form))


class NewsletterSubscribeAjaxView(View):
    """
    AJAX view for subscribing to the newsletter
    """
    def post(self, request):
        """Handle AJAX POST request"""
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()

            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email is required.'
                }, status=400)

            # Check if already subscribed
            if NewsletterSubscription.objects.filter(email=email, status='active').exists():
                return JsonResponse({
                    'success': False,
                    'message': 'This email is already subscribed to our newsletter.'
                }, status=400)

            # Create subscription
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={'status': 'active'}
            )

            if not created and subscription.status == 'unsubscribed':
                # Reactivate unsubscribed email
                subscription.status = 'active'
                subscription.unsubscribed_at = None
                subscription.save()

            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!'
            }, status=201)

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

class NewsletterUnsubscribeAjaxView(View):
    """
    AJAX view for unsubscribing from the newsletter
    """
    def post(self, request):
        """Handle AJAX POST request to unsubscribe"""
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
                        'message': 'You have been unsubscribed from our newsletter.'
                    }, status=200)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'This email is not currently subscribed.'
                    }, status=400)
            except NewsletterSubscription.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'This email is not found in our newsletter list.'
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

class NewsletterSuccessView(TemplateView):
    """
    Success page after newsletter subscription
    """
    template_name = 'notifications/subscribe/newsletter_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Newsletter Subscription Successful'
        return context
