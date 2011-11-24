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
    from objectapp.models import Objecttype
    tags_objecttype_published = Tag.objects.usage_for_queryset(
        Objecttype.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_objecttype_published])


class AuthorPublishedManager(models.Manager):
    """Manager to retrieve published authors"""

    def get_query_set(self):
        """Return published authors"""
        now = datetime.now()
        return super(AuthorPublishedManager, self).get_query_set().filter(
            objecttypes__status=PUBLISHED,
            objecttypes__start_publication__lte=now,
            objecttypes__end_publication__gt=now,
            objecttypes__sites=Site.objects.get_current()
            ).distinct()


def objecttypes_published(queryset):
    """Return only the objecttypes published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current())


class ObjecttypePublishedManager(models.Manager):
    """Manager to retrieve published objecttypes"""

    def get_query_set(self):
        """Return published objecttypes"""
        return objecttypes_published(
            super(ObjecttypePublishedManager, self).get_query_set())

    def on_site(self):
        """Return objecttypes published on current site"""
        return super(ObjecttypePublishedManager, self).get_query_set(
            ).filter(sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on objecttypes"""
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """Advanced search on objecttypes"""
        from objectapp.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """Basic search on objecttypes"""
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
