"""Placeholder model for Gstudio"""
from cms.models.fields import PlaceholderField

from gstudio.models import ObjecttypeAbstractClass


class ObjecttypePlaceholder(ObjecttypeAbstractClass):
    """Objecttype with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """ObjecttypePlaceholder's Meta"""
        abstract = True
