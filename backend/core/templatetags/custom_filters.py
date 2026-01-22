"""Custom template filters for core app.

Provides mathematical operations for use in templates.
"""
from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply the value by the argument.
    
    Usage: {{ product.price|mul:quantity }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide the value by the argument.
    
    Usage: {{ total|div:count }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
