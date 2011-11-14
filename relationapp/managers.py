"""Managers of Relationapp"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """Return the published tags"""
    from tagging.models import Tag
    from relationapp.models import Relationtype
    tags_relationtype_published = Tag.objects.usage_for_queryset(
        Relationtype.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_relationtype_published])


class AuthorPublishedManager(models.Manager):
    """Manager to retrieve published authors"""

    def get_query_set(self):
        """Return published authors"""
        now = datetime.now()
        return super(AuthorPublishedManager, self).get_query_set().filter(
            relationtypes__status=PUBLISHED,
            relationtypes__start_publication__lte=now,
            relationtypes__end_publication__gt=now,
            relationtypes__sites=Site.objects.get_current()
            ).distinct()


def relationtypes_published(queryset):
    """Return only the relationtypes published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current())


class RelationtypePublishedManager(models.Manager):
    """Manager to retrieve published relationtypes"""

    def get_query_set(self):
        """Return published relationtypes"""
        return relationtypes_published(
            super(RelationtypePublishedManager, self).get_query_set())

    def on_site(self):
        """Return relationtypes published on current site"""
        return super(RelationtypePublishedManager, self).get_query_set(
            ).filter(sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on relationtypes"""
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """Advanced search on relationtypes"""
        from relationapp.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """Basic search on relationtypes"""
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
