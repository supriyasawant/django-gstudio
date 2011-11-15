"""Placeholder model for Objectapp"""
from cms.models.fields import PlaceholderField

from objectapp.models import GBObject


class GBObjectPlaceholder(GBObject):
    """GBObject with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """GBObjectPlaceholder's Meta"""
        abstract = True
