"""Custom spam checker backend for testing Gstudio"""
from django.core.exceptions import ImproperlyConfigured


raise ImproperlyConfigured('This backend only exists for testing')


def backend(nodetype):
    """Custom spam checker backend for testing Gstudio"""
    return False
