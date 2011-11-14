"""Urls for the Objectapp feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.feeds import LatestGBObjects
from objectapp.feeds import GBObjectDiscussions
from objectapp.feeds import GBObjectComments
from objectapp.feeds import GBObjectTrackbacks
from objectapp.feeds import GBObjectPingbacks
from objectapp.feeds import SearchGBObjects
from objectapp.feeds import TagGBObjects
from objectapp.feeds import ObjecttypeGBObjects
from objectapp.feeds import AuthorGBObjects


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestGBObjects(),
        name='objectapp_gbobject_latest_feed'),
    url(r'^search/$',
        SearchGBObjects(),
        name='objectapp_gbobject_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagGBObjects(),
        name='objectapp_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorGBObjects(),
        name='objectapp_author_feed'),
    url(r'^objecttypes/(?P<path>[-\/\w]+)/$',
        ObjecttypeGBObjects(),
        name='objectapp_objecttype_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GBObjectDiscussions(),
        name='objectapp_gbobject_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GBObjectComments(),
        name='objectapp_gbobject_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GBObjectPingbacks(),
        name='objectapp_gbobject_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GBObjectTrackbacks(),
        name='objectapp_gbobject_trackback_feed'),
    )
