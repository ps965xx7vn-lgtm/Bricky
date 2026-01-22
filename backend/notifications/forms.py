"""Forms for notifications app.

Handles newsletter subscription form.
"""
from django import forms
from django.core.exceptions import ValidationError

from notifications.models import NewsletterSubscription


class NewsletterSubscriptionForm(forms.ModelForm):
    """Form for newsletter subscription."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        }),
        label='Email Address',
        help_text='We\'ll never share your email with anyone else.'
    )

    class Meta:
        model = NewsletterSubscription
        fields = ['email']

    def clean_email(self):
        """Validate email field."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email is required.')
        
        # Check if already subscribed
        if NewsletterSubscription.objects.filter(email=email, status='active').exists():
            raise ValidationError('This email is already subscribed to our newsletter.')
        
        return email

    def save(self, commit=True):
        """Save newsletter subscription."""
        instance = super().save(commit=False)
        instance.email = instance.email.lower().strip()
        if commit:
            instance.save()
        return instance
