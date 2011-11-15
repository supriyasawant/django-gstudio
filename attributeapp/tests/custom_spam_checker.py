"""Custom spam checker backend for testing Attributeapp"""
from django.core.exceptions import ImproperlyConfigured


raise ImproperlyConfigured('This backend only exists for testing')


def backend(attributetype):
    """Custom spam checker backend for testing Attributeapp"""
    return False
