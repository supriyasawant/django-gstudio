"""Sitemaps for Gstudio"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import TaggedItem

from gstudio.models import Objecttype
from gstudio.models import Author
from gstudio.models import Metatype
from gstudio.managers import tags_published


class ObjecttypeSitemap(Sitemap):
    """Sitemap for objecttypes"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published objecttypes"""
        return Objecttype.published.all()

    def lastmod(self, obj):
        """Return last modification of an objecttype"""
        return obj.last_update


class MetatypeSitemap(Sitemap):
    """Sitemap for metatypes"""
    changefreq = 'monthly'

    def cache(self, metatypes):
        """Cache categorie's objecttypes percent on total objecttypes"""
        len_objecttypes = float(Objecttype.published.count())
        self.cache_metatypes = {}
        for cat in metatypes:
            if len_objecttypes:
                self.cache_metatypes[cat.pk] = cat.objecttypes_published(
                    ).count() / len_objecttypes
            else:
                self.cache_metatypes[cat.pk] = 0.0

    def items(self):
        """Return all metatypes with coeff"""
        metatypes = Metatype.objects.all()
        self.cache(metatypes)
        return metatypes

    def lastmod(self, obj):
        """Return last modification of a metatype"""
        objecttypes = obj.objecttypes_published()
        if not objecttypes:
            return None
        return objecttypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_metatypes[obj.pk]
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
        objecttypes = obj.objecttypes_published()
        if not objecttypes:
            return None
        return objecttypes[0].creation_date

    def location(self, obj):
        """Return url of an author"""
        return reverse('gstudio_author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags):
        """Cache tag's objecttypes percent on total objecttypes"""
        len_objecttypes = float(Objecttype.published.count())
        self.cache_tags = {}
        for tag in tags:
            objecttypes = TaggedItem.objects.get_by_model(
                Objecttype.published.all(), tag)
            self.cache_tags[tag.pk] = (objecttypes, objecttypes.count() / len_objecttypes)

    def items(self):
        """Return all tags with coeff"""
        tags = tags_published()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        """Return last modification of a tag"""
        objecttypes = self.cache_tags[obj.pk][0]
        return objecttypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        """Return url of a tag"""
        return reverse('gstudio_tag_detail', args=[obj.name])
