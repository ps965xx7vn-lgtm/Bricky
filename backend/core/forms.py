from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage, NewsletterSubscription, Review


class ContactForm(forms.ModelForm):
    """
    Form for contact page submissions
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
        """Validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Name is required.')
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        if len(name) > 255:
            raise ValidationError('Name must be less than 255 characters.')
        return name

    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email is required.')
        return email

    def clean_phone(self):
        """Validate phone field"""
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and len(phone) < 5:
            raise ValidationError('Phone number is not valid.')
        return phone if phone else None

    def clean_message(self):
        """Validate message field"""
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise ValidationError('Message is required.')
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long.')
        if len(message) > 5000:
            raise ValidationError('Message must be less than 5000 characters.')
        return message

    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        return cleaned_data


class NewsletterSubscriptionForm(forms.ModelForm):
    """
    Form for newsletter subscription
    """
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
        """Validate email field"""
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email is required.')
        
        # Check if already subscribed
        if NewsletterSubscription.objects.filter(email=email, status='active').exists():
            raise ValidationError('This email is already subscribed to our newsletter.')
        
        return email

    def save(self, commit=True):
        """Save newsletter subscription"""
        instance = super().save(commit=False)
        instance.email = instance.email.lower().strip()
        if commit:
            instance.save()
        return instance


class ReviewForm(forms.ModelForm):
    """
    Form for product reviews
    """
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title',
                'required': True,
                'maxlength': '255'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this product...',
                'rows': 5,
                'required': True
            }),
            'rating': forms.HiddenInput(attrs={
                'class': 'review-rating-input',
                'value': '5'
            }),
        }

    def clean_title(self):
        """Validate review title"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Review title is required.')
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        if len(title) > 255:
            raise ValidationError('Title must be less than 255 characters.')
        return title

    def clean_content(self):
        """Validate review content"""
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise ValidationError('Review content is required.')
        if len(content) < 10:
            raise ValidationError('Review must be at least 10 characters long.')
        if len(content) > 5000:
            raise ValidationError('Review must be less than 5000 characters.')
        return content

    def clean_rating(self):
        """Validate rating"""
        rating = self.cleaned_data.get('rating')
        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                raise ValidationError('Rating must be between 1 and 5.')
            return rating_int
        except (ValueError, TypeError):
            raise ValidationError('Invalid rating.')
