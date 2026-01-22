"""Forms for store app.

Handles product reviews and ratings.
"""
from django import forms
from django.core.exceptions import ValidationError

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for product reviews."""
    
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
        """Validate review title."""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Review title is required.')
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        if len(title) > 255:
            raise ValidationError('Title must be less than 255 characters.')
        return title

    def clean_content(self):
        """Validate review content."""
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise ValidationError('Review content is required.')
        if len(content) < 10:
            raise ValidationError('Review must be at least 10 characters long.')
        if len(content) > 5000:
            raise ValidationError('Review must be less than 5000 characters.')
        return content

    def clean_rating(self):
        """Validate rating."""
        rating = self.cleaned_data.get('rating')
        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                raise ValidationError('Rating must be between 1 and 5.')
            return rating_int
        except (ValueError, TypeError):
            raise ValidationError('Invalid rating.')
