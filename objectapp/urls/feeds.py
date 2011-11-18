"""Urls for the Objectapp feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.feeds import LatestGbobjects
from objectapp.feeds import GbobjectDiscussions
from objectapp.feeds import GbobjectComments
from objectapp.feeds import GbobjectTrackbacks
from objectapp.feeds import GbobjectPingbacks
from objectapp.feeds import SearchGbobjects
from objectapp.feeds import TagGbobjects
from objectapp.feeds import ObjecttypeGbobjects
from objectapp.feeds import AuthorGbobjects


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestGbobjects(),
        name='objectapp_gbobject_latest_feed'),
    url(r'^search/$',
        SearchGbobjects(),
        name='objectapp_gbobject_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagGbobjects(),
        name='objectapp_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorGbobjects(),
        name='objectapp_author_feed'),
    url(r'^objecttypes/(?P<path>[-\/\w]+)/$',
        ObjecttypeGbobjects(),
        name='objectapp_Objecttype_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GbobjectDiscussions(),
        name='objectapp_gbobject_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GbobjectComments(),
        name='objectapp_gbobject_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GbobjectPingbacks(),
        name='objectapp_gbobject_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        GbobjectTrackbacks(),
        name='objectapp_gbobject_trackback_feed'),
    )
