"""ObjecttypeAdmin for Gstudio"""
from datetime import datetime

from django.forms import Media
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.conf import settings as project_settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

from tagging.models import Tag

import reversion
from gstudio import settings
from gstudio.managers import HIDDEN
from gstudio.managers import PUBLISHED
from gstudio.ping import DirectoryPinger
from gstudio.admin.forms import ObjecttypeAdminForm




class ObjecttypeAdmin(reversion.VersionAdmin):
    """Admin for Objecttype model"""
    form = ObjecttypeAdminForm
    date_hierarchy = 'creation_date'
    fieldsets = ((_('Content'), {'fields': ('title', 'content', 'parent',
                                            'image', 'status')}),
                 (_('Dependency'), {'fields': ('priornode', 'posteriornode',), 
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Discussion'), {'fields': ('comment_enabled',
                                               'pingback_enabled')}),
                 (_('Publication'), {'fields': ('metatypes', 'tags',
                                                'sites', 'slug')}))
    list_filter = ('parent','metatypes', 'authors', 'status', 'featured',
                   'login_required', 'comment_enabled', 'pingback_enabled',
                   'creation_date', 'start_publication',
                   'end_publication', 'sites')
    list_display = ('get_title', 'get_authors', 'get_metatypes',
                    'get_tags', 'get_sites',
                    'get_comments_are_open', 'pingback_enabled',
                    'get_is_actual', 'get_is_visible', 'get_link',
                    'get_short_url', 'creation_date')
    radio_fields = {'template': admin.VERTICAL}
    filter_horizontal = ('metatypes', 'authors', 'related')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'excerpt', 'content', 'tags')
    actions = ['make_mine', 'make_published', 'make_hidden',
               'close_comments', 'close_pingbacks',
               'ping_directories', 'make_tweet', 'put_on_top']
    actions_on_top = True
    actions_on_bottom = True

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(ObjecttypeAdmin, self).__init__(model, admin_site)

    # Custom Display
    def get_title(self, objecttype):
        """Return the title with word count and number of comments"""
        title = _('%(title)s (%(word_count)i words)') % \
                {'title': objecttype.title, 'word_count': objecttype.word_count}
        comments = objecttype.comments.count()
        if comments:
            return _('%(title)s (%(comments)i comments)') % \
                   {'title': title, 'comments': comments}
        return title
    get_title.short_description = _('title')

    def get_authors(self, objecttype):
        """Return the authors in HTML"""
        try:
            authors = ['<a href="%s" target="blank">%s</a>' %
                       (reverse('gstudio_author_detail',
                                args=[author.username]),
                        author.username) for author in objecttype.authors.all()]
        except NoReverseMatch:
            authors = [author.username for author in objecttype.authors.all()]
        return ', '.join(authors)
    get_authors.allow_tags = True
    get_authors.short_description = _('author(s)')

    def get_metatypes(self, objecttype):
        """Return the metatypes linked in HTML"""
        try:
            metatypes = ['<a href="%s" target="blank">%s</a>' %
                          (metatype.get_absolute_url(), metatype.title)
                          for metatype in objecttype.metatypes.all()]
        except NoReverseMatch:
            metatypes = [metatype.title for metatype in
                          objecttype.metatypes.all()]
        return ', '.join(metatypes)
    get_metatypes.allow_tags = True
    get_metatypes.short_description = _('metatype(s)')

    def get_tags(self, objecttype):
        """Return the tags linked in HTML"""
        try:
            return ', '.join(['<a href="%s" target="blank">%s</a>' %
                              (reverse('gstudio_tag_detail',
                                       args=[tag.name]), tag.name)
                              for tag in Tag.objects.get_for_object(objecttype)])
        except NoReverseMatch:
            return objecttype.tags
    get_tags.allow_tags = True
    get_tags.short_description = _('tag(s)')

    def get_sites(self, objecttype):
        """Return the sites linked in HTML"""
        return ', '.join(
            ['<a href="http://%(domain)s" target="blank">%(name)s</a>' %
             site.__dict__ for site in objecttype.sites.all()])
    get_sites.allow_tags = True
    get_sites.short_description = _('site(s)')

    def get_comments_are_open(self, objecttype):
        """Admin wrapper for objecttype.comments_are_open"""
        return objecttype.comments_are_open
    get_comments_are_open.boolean = True
    get_comments_are_open.short_description = _('comment enabled')

    def get_is_actual(self, objecttype):
        """Admin wrapper for objecttype.is_actual"""
        return objecttype.is_actual
    get_is_actual.boolean = True
    get_is_actual.short_description = _('is actual')

    def get_is_visible(self, objecttype):
        """Admin wrapper for objecttype.is_visible"""
        return objecttype.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    def get_link(self, objecttype):
        """Return a formated link to the objecttype"""
        return u'<a href="%s" target="blank">%s</a>' % (
            objecttype.get_absolute_url(), _('View'))
    get_link.allow_tags = True
    get_link.short_description = _('View on site')

    def get_short_url(self, objecttype):
        """Return the short url in HTML"""
        short_url = objecttype.short_url
        if not short_url:
            return _('Unavailable')
        return '<a href="%(url)s" target="blank">%(url)s</a>' % \
               {'url': short_url}
    get_short_url.allow_tags = True
    get_short_url.short_description = _('short url')

    # Custom Methods
    def save_model(self, request, objecttype, form, change):
        """Save the authors, update time, make an excerpt"""
        if not form.cleaned_data.get('excerpt') and objecttype.status == PUBLISHED:
            objecttype.excerpt = truncate_words(strip_tags(objecttype.content), 50)

        if objecttype.pk and not request.user.has_perm('gstudio.can_change_author'):
            form.cleaned_data['authors'] = objecttype.authors.all()

        if not form.cleaned_data.get('authors'):
            form.cleaned_data['authors'].append(request.user)

        objecttype.last_update = datetime.now()
        objecttype.save()

    def queryset(self, request):
        """Make special filtering by user permissions"""
        queryset = super(ObjecttypeAdmin, self).queryset(request)
        if request.user.has_perm('gstudio.can_view_all'):
            return queryset
        return request.user.objecttypes.all()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filters the disposable authors"""
        if db_field.name == 'authors':
            if request.user.has_perm('gstudio.can_change_author'):
                kwargs['queryset'] = User.objects.filter(is_staff=True)
            else:
                kwargs['queryset'] = User.objects.filter(pk=request.user.pk)

        return super(ObjecttypeAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_actions(self, request):
        """Define user actions by permissions"""
        actions = super(ObjecttypeAdmin, self).get_actions(request)
        if not request.user.has_perm('gstudio.can_change_author') \
           or not request.user.has_perm('gstudio.can_view_all'):
            del actions['make_mine']
        if not settings.PING_DIRECTORIES:
            del actions['ping_directories']
        if not settings.USE_TWITTER:
            del actions['make_tweet']

        return actions

    # Custom Actions
    def make_mine(self, request, queryset):
        """Set the objecttypes to the user"""
        for objecttype in queryset:
            if request.user not in objecttype.authors.all():
                objecttype.authors.add(request.user)
        self.message_user(
            request, _('The selected objecttypes now belong to you.'))
    make_mine.short_description = _('Set the objecttypes to the user')

    def make_published(self, request, queryset):
        """Set objecttypes selected as published"""
        queryset.update(status=PUBLISHED)
        self.ping_directories(request, queryset, messages=False)
        self.message_user(
            request, _('The selected objecttypes are now marked as published.'))
    make_published.short_description = _('Set objecttypes selected as published')

    def make_hidden(self, request, queryset):
        """Set objecttypes selected as hidden"""
        queryset.update(status=HIDDEN)
        self.message_user(
            request, _('The selected objecttypes are now marked as hidden.'))
    make_hidden.short_description = _('Set objecttypes selected as hidden')

    def make_tweet(self, request, queryset):
        """Post an update on Twitter"""
        import tweepy
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                   settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_KEY,
                              settings.TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        for objecttype in queryset:
            short_url = objecttype.short_url
            message = '%s %s' % (objecttype.title[:139 - len(short_url)], short_url)
            api.update_status(message)
        self.message_user(
            request, _('The selected objecttypes have been tweeted.'))
    make_tweet.short_description = _('Tweet objecttypes selected')

    def close_comments(self, request, queryset):
        """Close the comments for selected objecttypes"""
        queryset.update(comment_enabled=False)
        self.message_user(
            request, _('Comments are now closed for selected objecttypes.'))
    close_comments.short_description = _('Close the comments for '\
                                         'selected objecttypes')

    def close_pingbacks(self, request, queryset):
        """Close the pingbacks for selected objecttypes"""
        queryset.update(pingback_enabled=False)
        self.message_user(
            request, _('Linkbacks are now closed for selected objecttypes.'))
    close_pingbacks.short_description = _(
        'Close the linkbacks for selected objecttypes')

    def put_on_top(self, request, queryset):
        """Put the selected objecttypes on top at the current date"""
        queryset.update(creation_date=datetime.now())
        self.ping_directories(request, queryset, messages=False)
        self.message_user(request, _(
            'The selected objecttypes are now set at the current date.'))
    put_on_top.short_description = _(
        'Put the selected objecttypes on top at the current date')

    def ping_directories(self, request, queryset, messages=True):
        """Ping Directories for selected objecttypes"""
        for directory in settings.PING_DIRECTORIES:
            pinger = DirectoryPinger(directory, queryset)
            pinger.join()
            if messages:
                success = 0
                for result in pinger.results:
                    if not result.get('flerror', True):
                        success += 1
                    else:
                        self.message_user(request,
                                          '%s : %s' % (directory,
                                                       result['message']))
                if success:
                    self.message_user(
                        request,
                        _('%(directory)s directory succesfully ' \
                          'pinged %(success)d objecttypes.') %
                        {'directory': directory, 'success': success})
    ping_directories.short_description = _(
        'Ping Directories for selected objecttypes')

    def get_urls(self):
        objecttype_admin_urls = super(ObjecttypeAdmin, self).get_urls()
        urls = patterns(
            'django.views.generic.simple',
            url(r'^autocomplete_tags/$', 'direct_to_template',
                {'template': 'admin/gstudio/objecttype/autocomplete_tags.js',
                 'mimetype': 'application/javascript'},
                name='gstudio_objecttype_autocomplete_tags'),
            url(r'^wymeditor/$', 'direct_to_template',
                {'template': 'admin/gstudio/objecttype/wymeditor.js',
                 'mimetype': 'application/javascript'},
                name='gstudio_objecttype_wymeditor'),
            url(r'^markitup/$', 'direct_to_template',
                {'template': 'admin/gstudio/objecttype/markitup.js',
                 'mimetype': 'application/javascript'},
                name='gstudio_objecttype_markitup'),)
        return urls + objecttype_admin_urls

    def _media(self):
        STATIC_URL = '%sgstudio/' % project_settings.STATIC_URL
        media = super(ObjecttypeAdmin, self).media + Media(
            css={'all': ('%scss/jquery.autocomplete.css' % STATIC_URL,)},
            js=('%sjs/jquery.js' % STATIC_URL,
                '%sjs/jquery.bgiframe.js' % STATIC_URL,
                '%sjs/jquery.autocomplete.js' % STATIC_URL,
                reverse('admin:gstudio_objecttype_autocomplete_tags'),))

        if settings.WYSIWYG == 'wymeditor':
            media += Media(
                js=('%sjs/wymeditor/jquery.wymeditor.pack.js' % STATIC_URL,
                    '%sjs/wymeditor/plugins/hovertools/'
                    'jquery.wymeditor.hovertools.js' % STATIC_URL,
                    reverse('admin:gstudio_objecttype_wymeditor')))
        elif settings.WYSIWYG == 'tinymce':
            from tinymce.widgets import TinyMCE
            media += TinyMCE().media + Media(
                js=(reverse('tinymce-js', args=('admin/gstudio/objecttype',)),))
        elif settings.WYSIWYG == 'markitup':
            media += Media(
                js=('%sjs/markitup/jquery.markitup.js' % STATIC_URL,
                    '%sjs/markitup/sets/%s/set.js' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE),
                    reverse('admin:gstudio_objecttype_markitup')),
                css={'all': (
                    '%sjs/markitup/skins/django/style.css' % STATIC_URL,
                    '%sjs/markitup/sets/%s/style.css' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE))})
        return media
    media = property(_media)
