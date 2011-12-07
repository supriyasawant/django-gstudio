"""Placeholder model for Gstudio"""
from cms.models.fields import PlaceholderField

from gstudio.models import Nodetype


class NodetypePlaceholder(Nodetype):
    """Nodetype with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """NodetypePlaceholder's Meta"""
        abstract = True
