from typing import Any
import uuid

from django.conf import settings
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy

from users.forms import UserLoginForm, UserRegisterForm, ForgotPasswordForm, ResetPasswordForm, ProfileEditForm
from users.models import CustomUser
from orders.models import Order
from core.models import NewsletterSubscription


class LoginView(TemplateView):
    """
    View for user login
    POST: process login form
    GET: display login form
    """
    template_name = 'users/auth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['form'] = UserLoginForm(self.request.POST)
        else:
            context['form'] = UserLoginForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('core:index')
        return self.get(request, *args, **kwargs)


class RegisterView(TemplateView):
    """
    View for user registration
    POST: process registration form
    GET: display registration form
    """
    template_name = 'users/auth/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['form'] = UserRegisterForm(self.request.POST)
        else:
            context['form'] = UserRegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.is_active = True
            user.save()
            
            # Login the user first
            login(request, user)
            
            # Send verification email AFTER login
            # This ensures the token is generated with the correct last_login value
            send_verification(request, user)
            
            return redirect('core:index')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for user profile
    GET: display user profile information
    """
    template_name = 'users/profile/dashboard.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        
        # Get user's recent orders (latest 5)
        try:
            # Query orders through the customer relationship
            customer = user.customer
            orders = Order.objects.filter(customer=customer, is_draft=False).order_by('-registered_at')[:5]
            context['orders'] = orders
        except Exception as e:
            # Log error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not fetch orders for user {user.username}: {str(e)}")
            context['orders'] = []
        
        # Check if user is newsletter subscriber
        try:
            is_subscriber = NewsletterSubscription.objects.filter(email=user.email, status='active').exists()
            context['is_newsletter_subscriber'] = is_subscriber
        except:
            context['is_newsletter_subscriber'] = False
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing user profile
    GET: display edit profile form
    POST: process edit profile form
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
        # Handle password change if provided
        password = form.cleaned_data.get('password')
        if password:
            user.set_password(password)
        user.save()
        return super().form_valid(form)


def user_logout(request) -> Any:
    """
    View for user logout
    GET: log out the user and redirect to homepage
    """
    logout(request)
    return redirect('core:index')


def send_verification(request, user) -> Any:
    """
    Send email verification link to the user
    Uses Django's built-in token system which is reliable
    """
    try:
        # Ensure user is saved to database
        if not user.pk:
            user.save()
        
        # Generate token from fresh database fetch
        User = get_user_model()
        user = User.objects.get(pk=user.pk)
        
        # Use Django's default token generator
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        if isinstance(uid, bytes):
            uid = uid.decode()
        
        domain = get_current_site(request).domain
        
        # Build the verification link
        link = reverse("users:verify_email", kwargs={"uidb64": uid, "token": token})
        protocol = "https" if not settings.DEBUG else "http"
        verify_url = f"{protocol}://{domain}{link}"
        
        # Prepare email
        subject = "Email confirmation - Bricky"
        message = render_to_string("users/email/verify.html", {
            "user": user,
            "verify_url": verify_url,
            "domain": domain,
            "token": token,
        })

        # Send email
        send_mail(
            subject=subject, 
            message=message, 
            from_email=None, 
            recipient_list=[user.email], 
            html_message=message,
            fail_silently=False
        )
        print(f"✓ Verification email sent to {user.email}")
        
    except Exception as e:
        print(f"✗ Email error: {str(e)}")
        import traceback
        traceback.print_exc()


class EmailVerifyView(TemplateView):
    """
    View to verify user's email address
    Simple and reliable token validation
    """
    template_name = 'users/email/verified_success.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        import uuid as uuid_module
        User = get_user_model()
        
        try:
            # Decode the UID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid_module.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return render(request, 'users/email/verified_failed.html', {
                'error': 'Invalid verification link.',
                'show_resend': True
            })

        # Validate the token
        is_valid = default_token_generator.check_token(user, token)
        
        if is_valid:
            # Mark email as verified
            user.email_is_verified = True
            user.save(update_fields=['email_is_verified'])
            return render(request, 'users/email/verified_success.html', {
                'user': user,
                'message': 'Your email has been successfully verified!'
            })
        
        # Token is invalid or expired
        return render(request, 'users/email/verified_failed.html', {
            'error': 'The verification link is invalid or has expired.',
            'show_resend': True
        })




class ForgotPasswordView(TemplateView):
    """
    View for requesting password reset
    GET: display forgot password form
    POST: send password reset email
    """
    template_name = 'users/auth/forgot_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['form'] = ForgotPasswordForm(self.request.POST)
        else:
            context['form'] = ForgotPasswordForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = get_user_model().objects.get(email=email)
            
            try:
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                if isinstance(uid, bytes):
                    uid = uid.decode()
                
                domain = get_current_site(request).domain
                
                # Build the reset link
                link = reverse("users:reset_password", kwargs={"uidb64": uid, "token": token})
                protocol = "https" if not settings.DEBUG else "http"
                reset_url = f"{protocol}://{domain}{link}"
                
                # Prepare email
                subject = "Password Reset - Bricky"
                message = render_to_string("users/email/password_reset.html", {
                    "user": user,
                    "reset_url": reset_url,
                    "domain": domain,
                })
                
                # Send email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[user.email],
                    html_message=message,
                    fail_silently=False
                )
                
                context = self.get_context_data(**kwargs)
                context['message'] = 'Password reset link has been sent to your email. Please check your inbox.'
                context['message_type'] = 'success'
                return self.render_to_response(context)
            except Exception as e:
                context = self.get_context_data(**kwargs)
                context['message'] = f'Error sending email: {str(e)}'
                context['message_type'] = 'error'
                context['form'] = form
                return self.render_to_response(context)
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class ResetPasswordView(TemplateView):
    """
    View for resetting password with token
    GET: display reset password form
    POST: process password reset
    """
    template_name = 'users/auth/reset_password.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        import uuid as uuid_module
        User = get_user_model()
        
        try:
            # Decode the UID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid_module.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'Invalid password reset link.',
            })
        
        # Validate the token
        is_valid = default_token_generator.check_token(user, token)
        
        if not is_valid:
            return render(request, 'users/email/reset_failed.html', {
                'error': 'The password reset link is invalid or has expired.',
            })
        
        # Store the user ID and token in the session for POST
        request.session['reset_user_id'] = str(user.pk)
        request.session['reset_token'] = token
        
        context = {
            'form': ResetPasswordForm(),
            'uidb64': uidb64,
            'token': token,
        }
        return render(request, 'users/auth/reset_password.html', context)

    def post(self, request, uidb64, token, *args, **kwargs):
        import uuid as uuid_module
        User = get_user_model()
        
        try:
            # Decode the UID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uuid_module.UUID(uid))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'users/email/reset_failed.html', {
                'error': 'Invalid password reset link.',
            })
        
        # Validate the token
        is_valid = default_token_generator.check_token(user, token)
        
        if not is_valid:
            return render(request, 'users/email/reset_failed.html', {
                'error': 'The password reset link is invalid or has expired.',
            })
        
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save(update_fields=['password'])
            
            return render(request, 'users/email/reset_success.html', {
                'user': user,
                'message': 'Your password has been successfully reset! You can now login with your new password.',
            })
        
        context = {
            'form': form,
            'uidb64': uidb64,
            'token': token,
        }
        return render(request, 'users/auth/reset_password.html', context)

