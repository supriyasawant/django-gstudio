"""Sitemaps for Relationapp"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import TaggedItem

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import tags_published


class RelationtypeSitemap(Sitemap):
    """Sitemap for relationtypes"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published relationtypes"""
        return Relationtype.published.all()

    def lastmod(self, obj):
        """Return last modification of an relationtype"""
        return obj.last_update


class RelationSitemap(Sitemap):
    """Sitemap for relations"""
    changefreq = 'monthly'

    def cache(self, relations):
        """Cache categorie's relationtypes percent on total relationtypes"""
        len_relationtypes = float(Relationtype.published.count())
        self.cache_relations = {}
        for cat in relations:
            if len_relationtypes:
                self.cache_relations[cat.pk] = cat.relationtypes_published(
                    ).count() / len_relationtypes
            else:
                self.cache_relations[cat.pk] = 0.0

    def items(self):
        """Return all relations with coeff"""
        relations = Relation.objects.all()
        self.cache(relations)
        return relations

    def lastmod(self, obj):
        """Return last modification of a relation"""
        relationtypes = obj.relationtypes_published()
        if not relationtypes:
            return None
        return relationtypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_relations[obj.pk]
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
        relationtypes = obj.relationtypes_published()
        if not relationtypes:
            return None
        return relationtypes[0].creation_date

    def location(self, obj):
        """Return url of an author"""
        return reverse('relationapp_author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags):
        """Cache tag's relationtypes percent on total relationtypes"""
        len_relationtypes = float(Relationtype.published.count())
        self.cache_tags = {}
        for tag in tags:
            relationtypes = TaggedItem.objects.get_by_model(
                Relationtype.published.all(), tag)
            self.cache_tags[tag.pk] = (relationtypes, relationtypes.count() / len_relationtypes)

    def items(self):
        """Return all tags with coeff"""
        tags = tags_published()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        """Return last modification of a tag"""
        relationtypes = self.cache_tags[obj.pk][0]
        return relationtypes[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        """Return url of a tag"""
        return reverse('relationapp_tag_detail', args=[obj.name])
