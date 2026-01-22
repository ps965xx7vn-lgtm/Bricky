"""Views for users app.

Handles user authentication (login, register, logout), profile management,
email verification, and password reset functionality.
"""
import uuid
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy

from users.forms import (
    UserLoginForm, UserRegisterForm, 
    ForgotPasswordForm, ResetPasswordForm, ProfileEditForm
)
from users.models import CustomUser
from users.utils import send_verification_email, send_password_reset_email
from orders.models import Order
from notifications.models import NewsletterSubscription


# ===== Authentication Views =====

class LoginView(TemplateView):
    """Handle user login.
    
    GET: Display login form
    POST: Authenticate user and redirect to home
    """
    template_name = 'users/auth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserLoginForm(self.request.POST or None)
        return context

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('store:index')
        return self.get(request, *args, **kwargs)


class RegisterView(TemplateView):
    """Handle user registration.
    
    GET: Display registration form
    POST: Create new user account and send verification email
    """
    template_name = 'users/auth/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserRegisterForm(self.request.POST or None)
        return context

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("password"))
            user.is_active = True
            user.save()
            
            # Login user and send verification email
            login(request, user)
            send_verification_email(request, user)
            
            return redirect('store:index')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


def user_logout(request):
    """Log out current user and redirect to home page.
    
    Function-based view for simplicity.
    """
    logout(request)
    return redirect('store:index')


# ===== Profile Views =====

class ProfileView(LoginRequiredMixin, TemplateView):
    """Display user profile dashboard.
    
    Shows:
    - User information
    - Recent orders (last 5)
    - Newsletter subscription status
    """
    template_name = 'users/profile/dashboard.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent orders
        try:
            customer = user.customer
            context['orders'] = Order.objects.filter(
                customer=customer,
                is_draft=False
            ).order_by('-registered_at')[:5]
        except:
            context['orders'] = []
        
        # Newsletter subscription status
        context['is_newsletter_subscriber'] = NewsletterSubscription.objects.filter(
            email=user.email,
            status='active'
        ).exists()
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile information.
    
    Allows updating:
    - Personal information
    - Email address
    - Password (optional)
    """
    model = CustomUser
    template_name = 'users/profile/edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('users:profile')
    login_url = 'users:login'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        
        # Update password if provided
        password = form.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        return super().form_valid(form)


# ===== Email Verification Views =====

class EmailVerifyView(TemplateView):
    """Verify user email address via token link.
    
    Validates token from email link and marks email as verified.
    Shows success or failure page based on token validity.
    """
    template_name = 'users/email/verified_success.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        
        try:
            # Decode UID and get user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'users/email/verified_failed.html', {
                'error': 'Invalid verification link.',
                'show_resend': True
            })

        # Validate token
        if default_token_generator.check_token(user, token):
            user.email_is_verified = True
            user.save(update_fields=['email_is_verified'])
            return render(request, 'users/email/verified_success.html', {
                'user': user,
                'message': 'Your email has been successfully verified!'
            })
        
        return render(request, 'users/email/verified_failed.html', {
            'error': 'The verification link is invalid or expired.',
            'show_resend': True
        })


# ===== Password Reset Views =====

class ForgotPasswordView(TemplateView):
    """Request password reset link.
    
    GET: Display email input form
    POST: Send password reset email with token link
    """
    template_name = 'users/auth/forgot_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ForgotPasswordForm(self.request.POST or None)
        return context

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        context = self.get_context_data(**kwargs)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = get_user_model().objects.get(email=email)
            
            if send_password_reset_email(request, user):
                context['message'] = 'Password reset link sent to your email.'
                context['message_type'] = 'success'
            else:
                context['message'] = 'Error sending email. Please try again.'
                context['message_type'] = 'error'
        
        context['form'] = form
        return self.render_to_response(context)


class ResetPasswordView(TemplateView):
    """Reset password with token.
    
    GET: Validate token and display password reset form
    POST: Process new password and update user account
    
    Token expires after 24 hours (configurable in settings).
    """
    template_name = 'users/auth/reset_password.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        
        try:
            # Decode and validate
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'Invalid password reset link.'
            })
        
        if not default_token_generator.check_token(user, token):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'The password reset link is invalid or expired.'
            })
        
        # Store for POST
        request.session['reset_user_id'] = str(user.pk)
        request.session['reset_token'] = token
        
        return render(request, self.template_name, {
            'form': ResetPasswordForm(),
            'uidb64': uidb64,
            'token': token,
        })

    def post(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'Invalid password reset link.'
            })
        
        if not default_token_generator.check_token(user, token):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'The password reset link is invalid or expired.'
            })
        
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save(update_fields=['password'])
            
            return render(request, 'users/email/reset_success.html', {
                'user': user,
                'message': 'Password reset successful! You can now login.'
            })
        
        return render(request, self.template_name, {
            'form': form,
            'uidb64': uidb64,
            'token': token,
        })
