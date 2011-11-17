"""Sitemaps for Objectapp"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import TaggedItem

from objectapp.models import Gbobject
from objectapp.models import Author
from objectapp.models import Objecttype
from objectapp.managers import tags_published


class GbobjectSitemap(Sitemap):
    """Sitemap for gbobjects"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published gbobjects"""
        return Gbobject.published.all()

    def lastmod(self, obj):
        """Return last modification of an gbobject"""
        return obj.last_update


class ObjecttypeSitemap(Sitemap):
    """Sitemap for objecttypes"""
    changefreq = 'monthly'

    def cache(self, objecttypes):
        """Cache categorie's gbobjects percent on total gbobjects"""
        len_gbobjects = float(Gbobject.published.count())
        self.cache_objecttypes = {}
        for cat in objecttypes:
            if len_gbobjects:
                self.cache_objecttypes[cat.pk] = cat.gbobjects_published(
                    ).count() / len_gbobjects
            else:
                self.cache_objecttypes[cat.pk] = 0.0

    def items(self):
        """Return all objecttypes with coeff"""
        objecttypes = Objecttype.objects.all()
        self.cache(objecttypes)
        return objecttypes

    def lastmod(self, obj):
        """Return last modification of a Objecttype"""
        gbobjects = obj.gbobjects_published()
        if not gbobjects:
            return None
        return gbobjects[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_objecttypes[obj.pk]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority


class AuthorSitemap(Sitemap):
    """Sitemap for authors"""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        """Return published authors"""
        return Author.published.all()

    def lastmod(self, obj):
        """Return last modification of an author"""
        gbobjects = obj.gbobjects_published()
        if not gbobjects:
            return None
        return gbobjects[0].creation_date

    def location(self, obj):
        """Return url of an author"""
        return reverse('objectapp_author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags):
        """Cache tag's gbobjects percent on total gbobjects"""
        len_gbobjects = float(Gbobject.published.count())
        self.cache_tags = {}
        for tag in tags:
            gbobjects = TaggedItem.objects.get_by_model(
                Gbobject.published.all(), tag)
            self.cache_tags[tag.pk] = (gbobjects, gbobjects.count() / len_gbobjects)

    def items(self):
        """Return all tags with coeff"""
        tags = tags_published()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        """Return last modification of a tag"""
        gbobjects = self.cache_tags[obj.pk][0]
        return gbobjects[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        """Return url of a tag"""
        return reverse('objectapp_tag_detail', args=[obj.name])
