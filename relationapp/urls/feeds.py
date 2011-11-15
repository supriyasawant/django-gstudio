"""Urls for the Relationapp feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from relationapp.feeds import LatestRelationtypes
from relationapp.feeds import RelationtypeDiscussions
from relationapp.feeds import RelationtypeComments
from relationapp.feeds import RelationtypeTrackbacks
from relationapp.feeds import RelationtypePingbacks
from relationapp.feeds import SearchRelationtypes
from relationapp.feeds import TagRelationtypes
from relationapp.feeds import RelationRelationtypes
from relationapp.feeds import AuthorRelationtypes


urlpatterns = patterns(
    '',
    url(r'^latest/$',
        LatestRelationtypes(),
        name='relationapp_relationtype_latest_feed'),
    url(r'^search/$',
        SearchRelationtypes(),
        name='relationapp_relationtype_search_feed'),
    url(r'^tags/(?P<slug>[- \w]+)/$',
        TagRelationtypes(),
        name='relationapp_tag_feed'),
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        AuthorRelationtypes(),
        name='relationapp_author_feed'),
    url(r'^relations/(?P<path>[-\/\w]+)/$',
        RelationRelationtypes(),
        name='relationapp_relation_feed'),
    url(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        RelationtypeDiscussions(),
        name='relationapp_relationtype_discussion_feed'),
    url(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        RelationtypeComments(),
        name='relationapp_relationtype_comment_feed'),
    url(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        RelationtypePingbacks(),
        name='relationapp_relationtype_pingback_feed'),
    url(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/' \
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        RelationtypeTrackbacks(),
        name='relationapp_relationtype_trackback_feed'),
    )
