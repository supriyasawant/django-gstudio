"""Managers of Attributeapp"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """Return the published tags"""
    from tagging.models import Tag
    from attributeapp.models import Attributetype
    tags_attributetype_published = Tag.objects.usage_for_queryset(
        Attributetype.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_attributetype_published])


class AuthorPublishedManager(models.Manager):
    """Manager to retrieve published authors"""

    def get_query_set(self):
        """Return published authors"""
        now = datetime.now()
        return super(AuthorPublishedManager, self).get_query_set().filter(
            attributetypes__status=PUBLISHED,
            attributetypes__start_publication__lte=now,
            attributetypes__end_publication__gt=now,
            attributetypes__sites=Site.objects.get_current()
            ).distinct()


def attributetypes_published(queryset):
    """Return only the attributetypes published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current())


class AttributetypePublishedManager(models.Manager):
    """Manager to retrieve published attributetypes"""

    def get_query_set(self):
        """Return published attributetypes"""
        return attributetypes_published(
            super(AttributetypePublishedManager, self).get_query_set())

    def on_site(self):
        """Return attributetypes published on current site"""
        return super(AttributetypePublishedManager, self).get_query_set(
            ).filter(sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on attributetypes"""
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """Advanced search on attributetypes"""
        from attributeapp.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """Basic search on attributetypes"""
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
