"""Sitemaps for Attributeapp"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import TaggedItem

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.models import Attribute
from attributeapp.managers import tags_published


class AttributetypeSitemap(Sitemap):
    """Sitemap for attributetypes"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published attributetypes"""
        return Attributetype.published.all()

    def lastmod(self, obj):
        """Return last modification of an attributetype"""
        return obj.last_update


class AttributeSitemap(Sitemap):
    """Sitemap for attributes"""
    changefreq = 'monthly'

    def cache(self, attributes):
        """Cache categorie's attributetypes percent on total attributetypes"""
        len_attributetypes = float(Attributetype.published.count())
        self.cache_attributes = {}
        for cat in attributes:
            if len_attributetypes:
                self.cache_attributes[cat.pk] = cat.attributetypes_published(
                    ).count() / len_attributetypes
            else:
                self.cache_attributes[cat.pk] = 0.0

    def items(self):
        """Return all attributes with coeff"""
        attributes = Attribute.objects.all()
        self.cache(attributes)
        return attributes

    def lastmod(self, obj):
        """Return last modification of a attribute"""
        attributetypes = obj.attributetypes_published()
        if not attributetypes:
            return None
        return attributetypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_attributes[obj.pk]
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
        attributetypes = obj.attributetypes_published()
        if not attributetypes:
            return None
        return attributetypes[0].creation_date

    def location(self, obj):
        """Return url of an author"""
        return reverse('attributeapp_author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags):
        """Cache tag's attributetypes percent on total attributetypes"""
        len_attributetypes = float(Attributetype.published.count())
        self.cache_tags = {}
        for tag in tags:
            attributetypes = TaggedItem.objects.get_by_model(
                Attributetype.published.all(), tag)
            self.cache_tags[tag.pk] = (attributetypes, attributetypes.count() / len_attributetypes)

    def items(self):
        """Return all tags with coeff"""
        tags = tags_published()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        """Return last modification of a tag"""
        attributetypes = self.cache_tags[obj.pk][0]
        return attributetypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        """Return url of a tag"""
        return reverse('attributeapp_tag_detail', args=[obj.name])
