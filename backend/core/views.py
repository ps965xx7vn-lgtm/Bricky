from django.shortcuts import  redirect
from django.views.generic import ListView, TemplateView
from django.db.models import Q
from django.contrib import messages

from .models import ContactMessage
from .forms import ContactForm
from store.models import Product, Category


# ============ HOME PAGE VIEW ============

class IndexView(ListView):
    """
    Store main page showing all products with filters and categories
    """
    model = Product
    template_name = 'core/index.html'
    context_object_name = 'object_list'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort'] = self.request.GET.get('sort', '-created_at')
        
        # Price range for filter
        products = Product.objects.filter(is_active=True)
        if products.exists():
            context['price_max'] = products.order_by('-price').first().price
            context['price_min'] = products.order_by('price').first().price
        
        return context


# ============ LEGAL & INFO PAGES ============
class PrivacyPolicyView(TemplateView):
    """
    View for displaying the Privacy Policy page
    """
    template_name = 'core/legal/privacy.html'


class TermsOfServiceView(TemplateView):
    """
    View for displaying the Terms of Service page
    """
    template_name = 'core/legal/terms.html'


class AboutView(TemplateView):
    """
    View for displaying the About page
    """
    template_name = 'core/pages/about.html'


class ContactView(TemplateView):
    """
    View for displaying and handling the Contact page form
    """
    template_name = 'core/pages/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        context['subject_choices'] = ContactMessage.SubjectChoice.choices
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission"""
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Save the contact message
            contact_message = form.save()
            
            messages.success(
                request,
                f'Thank you for your message! We will get back to you at {contact_message.email} within 24 business hours.'
            )
            
            # Redirect to same page to clear form
            return redirect('core:contact')
        else:
            # Return with form errors
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)

