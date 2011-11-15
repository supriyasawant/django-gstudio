"""Urls for the Attributeapp feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from attributeapp.feeds import LatestAttributetypes
from attributeapp.feeds import AttributetypeDiscussions
from attributeapp.feeds import AttributetypeComments
from attributeapp.feeds import AttributetypeTrackbacks
from attributeapp.feeds import AttributetypePingbacks
from attributeapp.feeds import SearchAttributetypes
from attributeapp.feeds import TagAttributetypes
from attributeapp.feeds import AttributeAttributetypes
from attributeapp.feeds import AuthorAttributetypes


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestAttributetypes(),
        name='attributeapp_attributetype_latest_feed'),
    url(r'^search/$',
        SearchAttributetypes(),
        name='attributeapp_attributetype_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagAttributetypes(),
        name='attributeapp_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorAttributetypes(),
        name='attributeapp_author_feed'),
    url(r'^attributes/(?P<path>[-\/\w]+)/$',
        AttributeAttributetypes(),
        name='attributeapp_attribute_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        AttributetypeDiscussions(),
        name='attributeapp_attributetype_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        AttributetypeComments(),
        name='attributeapp_attributetype_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        AttributetypePingbacks(),
        name='attributeapp_attributetype_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        AttributetypeTrackbacks(),
        name='attributeapp_attributetype_trackback_feed'),
    )
