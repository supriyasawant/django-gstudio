"""Custom url shortener backend for testing Gstudio"""
from django.core.exceptions import ImproperlyConfigured


raise ImproperlyConfigured('This backend only exists for testing')


def backend(objecttype):
    """Custom url shortener backend for testing Gstudio"""
    return ''
