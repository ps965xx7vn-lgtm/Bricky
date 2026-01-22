"""Forms for core app.

Handles contact form submissions from visitors.
"""
from django import forms
from django.core.exceptions import ValidationError

from .models import ContactMessage


# ===== Contact Form =====

class ContactForm(forms.ModelForm):
    """Form for contact page submissions.
    
    Validates user input and creates ContactMessage records.
    All fields except phone are required.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+90 (XXX) XXX-XXXX',
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us how we can help...',
                'rows': 6,
                'required': True
            }),
        }

    def clean_name(self):
        """Validate name field."""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Name is required.')
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        if len(name) > 255:
            raise ValidationError('Name must be less than 255 characters.')
        return name

    def clean_email(self):
        """Validate email field."""
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email is required.')
        return email

    def clean_phone(self):
        """Validate phone field (optional)."""
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and len(phone) < 5:
            raise ValidationError('Phone number is not valid.')
        return phone if phone else None

    def clean_message(self):
        """Validate message field."""
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise ValidationError('Message is required.')
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long.')
        if len(message) > 5000:
            raise ValidationError('Message must be less than 5000 characters.')
        return message

    def clean(self):
        """Additional cross-field validation."""
        cleaned_data = super().clean()
        return cleaned_data

