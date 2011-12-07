"""Urls for the Gstudio feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from gstudio.feeds import LatestNodetypes
from gstudio.feeds import NodetypeDiscussions
from gstudio.feeds import NodetypeComments
from gstudio.feeds import NodetypeTrackbacks
from gstudio.feeds import NodetypePingbacks
from gstudio.feeds import SearchNodetypes
from gstudio.feeds import TagNodetypes
from gstudio.feeds import MetatypeNodetypes
from gstudio.feeds import AuthorNodetypes


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestNodetypes(),
        name='gstudio_nodetype_latest_feed'),
    url(r'^search/$',
        SearchNodetypes(),
        name='gstudio_nodetype_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagNodetypes(),
        name='gstudio_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorNodetypes(),
        name='gstudio_author_feed'),
    url(r'^metatypes/(?P<path>[-\/\w]+)/$',
        MetatypeNodetypes(),
        name='gstudio_metatype_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        NodetypeDiscussions(),
        name='gstudio_nodetype_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        NodetypeComments(),
        name='gstudio_nodetype_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        NodetypePingbacks(),
        name='gstudio_nodetype_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        NodetypeTrackbacks(),
        name='gstudio_nodetype_trackback_feed'),
    )
