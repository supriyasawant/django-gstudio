"""Placeholder model for Relationapp"""
from cms.models.fields import PlaceholderField

from relationapp.models import Relationtype


class RelationtypePlaceholder(Relationtype):
    """Relationtype with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """RelationtypePlaceholder's Meta"""
        abstract = True
