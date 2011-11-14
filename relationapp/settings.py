"""Settings of Relationapp"""
from django.conf import settings

PING_DIRECTORIES = getattr(settings, 'RELATIONAPP_PING_DIRECTORIES',
                           ('http://django-relationapp.com/xmlrpc/',))
SAVE_PING_DIRECTORIES = getattr(settings, 'RELATIONAPP_SAVE_PING_DIRECTORIES',
                                bool(PING_DIRECTORIES))
SAVE_PING_EXTERNAL_URLS = getattr(settings, 'RELATIONAPP_PING_EXTERNAL_URLS', True)

COPYRIGHT = getattr(settings, 'RELATIONAPP_COPYRIGHT', 'Relationapp')

PAGINATION = getattr(settings, 'RELATIONAPP_PAGINATION', 10)
ALLOW_EMPTY = getattr(settings, 'RELATIONAPP_ALLOW_EMPTY', True)
ALLOW_FUTURE = getattr(settings, 'RELATIONAPP_ALLOW_FUTURE', True)

RELATIONTYPE_TEMPLATES = getattr(settings, 'RELATIONAPP_RELATIONTYPE_TEMPLATES', [])
RELATIONTYPE_BASE_MODEL = getattr(settings, 'RELATIONAPP_RELATIONTYPE_BASE_MODEL', '')

MARKUP_LANGUAGE = getattr(settings, 'RELATIONAPP_MARKUP_LANGUAGE', 'html')

MARKDOWN_EXTENSIONS = getattr(settings, 'RELATIONAPP_MARKDOWN_EXTENSIONS', '')

WYSIWYG_MARKUP_MAPPING = {
    'textile': 'markitup',
    'markdown': 'markitup',
    'restructuredtext': 'markitup',
    'html': 'tinymce' in settings.INSTALLED_APPS and 'tinymce' or 'wymeditor'}

WYSIWYG = getattr(settings, 'RELATIONAPP_WYSIWYG',
                  WYSIWYG_MARKUP_MAPPING.get(MARKUP_LANGUAGE))

AUTO_CLOSE_COMMENTS_AFTER = getattr(
    settings, 'RELATIONAPP_AUTO_CLOSE_COMMENTS_AFTER', None)

AUTO_MODERATE_COMMENTS = getattr(settings, 'RELATIONAPP_AUTO_MODERATE_COMMENTS',
                                 False)

MAIL_COMMENT_REPLY = getattr(settings, 'RELATIONAPP_MAIL_COMMENT_REPLY', False)

MAIL_COMMENT_AUTHORS = getattr(settings, 'RELATIONAPP_MAIL_COMMENT_AUTHORS', True)

MAIL_COMMENT_NOTIFICATION_RECIPIENTS = getattr(
    settings, 'RELATIONAPP_MAIL_COMMENT_NOTIFICATION_RECIPIENTS',
    [manager_tuple[1] for manager_tuple in settings.MANAGERS])

UPLOAD_TO = getattr(settings, 'RELATIONAPP_UPLOAD_TO', 'uploads')

PROTOCOL = getattr(settings, 'RELATIONAPP_PROTOCOL', 'http')

FEEDS_FORMAT = getattr(settings, 'RELATIONAPP_FEEDS_FORMAT', 'rss')
FEEDS_MAX_ITEMS = getattr(settings, 'RELATIONAPP_FEEDS_MAX_ITEMS', 15)

PINGBACK_CONTENT_LENGTH = getattr(settings,
                                  'RELATIONAPP_PINGBACK_CONTENT_LENGTH', 300)

F_MIN = getattr(settings, 'RELATIONAPP_F_MIN', 0.1)
F_MAX = getattr(settings, 'RELATIONAPP_F_MAX', 1.0)

SPAM_CHECKER_BACKENDS = getattr(settings, 'RELATIONAPP_SPAM_CHECKER_BACKENDS',
                                ())

URL_SHORTENER_BACKEND = getattr(settings, 'RELATIONAPP_URL_SHORTENER_BACKEND',
                                'relationapp.url_shortener.backends.default')

STOP_WORDS = getattr(settings, 'RELATIONAPP_STOP_WORDS',
                     ('able', 'about', 'across', 'after', 'all', 'almost',
                      'also', 'among', 'and', 'any', 'are', 'because', 'been',
                      'but', 'can', 'cannot', 'could', 'dear', 'did', 'does',
                      'either', 'else', 'ever', 'every', 'for', 'from', 'get',
                      'got', 'had', 'has', 'have', 'her', 'hers', 'him', 'his',
                      'how', 'however', 'into', 'its', 'just', 'least', 'let',
                      'like', 'likely', 'may', 'might', 'most', 'must',
                      'neither', 'nor', 'not', 'off', 'often', 'only', 'other',
                      'our', 'own', 'rather', 'said', 'say', 'says', 'she',
                      'should', 'since', 'some', 'than', 'that', 'the',
                      'their', 'them', 'then', 'there', 'these', 'they',
                      'this', 'tis', 'too', 'twas', 'wants', 'was', 'were',
                      'what', 'when', 'where', 'which', 'while', 'who', 'whom',
                      'why', 'will', 'with', 'would', 'yet', 'you', 'your'))

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
TWITTER_ACCESS_KEY = getattr(settings, 'TWITTER_ACCESS_KEY', '')
TWITTER_ACCESS_SECRET = getattr(settings, 'TWITTER_ACCESS_SECRET', '')

USE_TWITTER = getattr(settings, 'RELATIONAPP_USE_TWITTER',
                      bool(TWITTER_ACCESS_KEY and TWITTER_ACCESS_SECRET and \
                           TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET))
