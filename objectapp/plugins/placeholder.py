"""Placeholder model for Objectapp"""
from cms.models.fields import PlaceholderField

from objectapp.models import GbobjectAbstractClass


class GbobjectPlaceholder(GbobjectAbstractClass):
    """Gbobject with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """GbobjectPlaceholder's Meta"""
        abstract = True
