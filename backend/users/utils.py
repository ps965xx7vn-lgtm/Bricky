"""Utility functions for users app.

Provides email sending functionality for:
- Email verification during registration
- Password reset requests
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# ===== Email Verification =====

def send_verification_email(request, user):
    """Send email verification link to user.
    
    Args:
        request: HTTP request object for domain detection
        user: CustomUser instance to send verification to
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Ensure user is saved
        if not user.pk:
            user.save()
        
        # Get fresh user from database
        User = get_user_model()
        user = User.objects.get(pk=user.pk)
        
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        if isinstance(uid, bytes):
            uid = uid.decode()
        
        # Build verification URL
        domain = get_current_site(request).domain
        link = reverse("users:verify_email", kwargs={"uidb64": uid, "token": token})
        protocol = "https" if not settings.DEBUG else "http"
        verify_url = f"{protocol}://{domain}{link}"
        
        # Send email
        subject = "Email confirmation - Bricky"
        message = render_to_string("users/email/verify.html", {
            "user": user,
            "verify_url": verify_url,
            "domain": domain,
        })

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False
        )
        
        return True
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Email error: {e}", exc_info=True)
        return False


# ===== Password Reset =====

def send_password_reset_email(request, user):
    """Send password reset link to user.
    
    Args:
        request: HTTP request object for domain detection
        user: CustomUser instance to send reset link to
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        if isinstance(uid, bytes):
            uid = uid.decode()
        
        # Build reset URL
        domain = get_current_site(request).domain
        link = reverse("users:reset_password", kwargs={"uidb64": uid, "token": token})
        protocol = "https" if not settings.DEBUG else "http"
        reset_url = f"{protocol}://{domain}{link}"
        
        # Send email
        subject = "Password Reset - Bricky"
        message = render_to_string("users/email/password_reset.html", {
            "user": user,
            "reset_url": reset_url,
            "domain": domain,
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False
        )
        
        return True
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Email error: {e}", exc_info=True)
        return False
