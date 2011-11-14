"""Placeholder model for Attributeapp"""
from cms.models.fields import PlaceholderField

from attributeapp.models import Attributetype


class AttributetypePlaceholder(Attributetype):
    """Attributetype with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """AttributetypePlaceholder's Meta"""
        abstract = True
