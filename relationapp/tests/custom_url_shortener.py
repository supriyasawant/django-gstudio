"""Custom url shortener backend for testing Relationapp"""
from django.core.exceptions import ImproperlyConfigured


raise ImproperlyConfigured('This backend only exists for testing')


def backend(relationtype):
    """Custom url shortener backend for testing Relationapp"""
    return ''
