"""Urls for the Gstudio feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from gstudio.feeds import LatestObjecttypes
from gstudio.feeds import ObjecttypeDiscussions
from gstudio.feeds import ObjecttypeComments
from gstudio.feeds import ObjecttypeTrackbacks
from gstudio.feeds import ObjecttypePingbacks
from gstudio.feeds import SearchObjecttypes
from gstudio.feeds import TagObjecttypes
from gstudio.feeds import MetatypeObjecttypes
from gstudio.feeds import AuthorObjecttypes


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestObjecttypes(),
        name='gstudio_objecttype_latest_feed'),
    url(r'^search/$',
        SearchObjecttypes(),
        name='gstudio_objecttype_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagObjecttypes(),
        name='gstudio_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorObjecttypes(),
        name='gstudio_author_feed'),
    url(r'^metatypes/(?P<path>[-\/\w]+)/$',
        MetatypeObjecttypes(),
        name='gstudio_metatype_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        ObjecttypeDiscussions(),
        name='gstudio_objecttype_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        ObjecttypeComments(),
        name='gstudio_objecttype_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        ObjecttypePingbacks(),
        name='gstudio_objecttype_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        ObjecttypeTrackbacks(),
        name='gstudio_objecttype_trackback_feed'),
    )
