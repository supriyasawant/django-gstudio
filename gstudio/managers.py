"""Managers of gstudio"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """Return the published tags"""
    from tagging.models import Tag
    from gstudio.models import Nodetype
    tags_nodetype_published = Tag.objects.usage_for_queryset(
        Nodetype.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_nodetype_published])


class AuthorPublishedManager(models.Manager):
    """Manager to retrieve published authors"""

    def get_query_set(self):
        """Return published authors"""
        now = datetime.now()
        return super(AuthorPublishedManager, self).get_query_set().filter(
            nodetypes__status=PUBLISHED,
            nodetypes__start_publication__lte=now,
            nodetypes__end_publication__gt=now,
            nodetypes__sites=Site.objects.get_current()
            ).distinct()


def nodetypes_published(queryset):

    """Return only the nodetypes published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current())


class NodetypePublishedManager(models.Manager):
    """Manager to retrieve published nodetypes"""

    def get_query_set(self):
        """Return published nodetypes"""
        return nodetypes_published(
            super(NodetypePublishedManager, self).get_query_set())

    def on_site(self):
        """Return nodetypes published on current site"""
        return super(NodetypePublishedManager, self).get_query_set(
            ).filter(sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on nodetypes"""
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """Advanced search on nodetypes"""
        from gstudio.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """Basic search on nodetypes"""
        lookup = None
        for pattern in pattern.split():
            query_part = models.Q(content__icontains=pattern) | \
                         models.Q(excerpt__icontains=pattern) | \
                         models.Q(title__icontains=pattern)
            if lookup is None:
                lookup = query_part
            else:
                lookup |= query_part

        return self.get_query_set().filter(lookup)
