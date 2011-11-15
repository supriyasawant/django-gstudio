"""Signal handlers of Attributeapp"""
import inspect
from functools import wraps

from django.db.models.signals import post_save

from attributeapp import settings


def disable_for_loaddata(signal_handler):
    """Decorator for disabling signals sent
    by 'post_save' on loaddata command.
    http://code.djangoproject.com/ticket/8399"""

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return
        signal_handler(*args, **kwargs)

    return wrapper


@disable_for_loaddata
def ping_directories_handler(sender, **kwargs):
    """Ping Directories when an attributetype is saved"""
    attributetype = kwargs['instance']

    if attributetype.is_visible and settings.SAVE_PING_DIRECTORIES:
        from attributeapp.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [attributetype])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """Ping Externals URLS when an attributetype is saved"""
    attributetype = kwargs['instance']

    if attributetype.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from attributeapp.ping import ExternalUrlsPinger

        ExternalUrlsPinger(attributetype)


def disconnect_attributeapp_signals():
    """Disconnect all the signals provided by Attributeapp"""
    from attributeapp.models import Attributetype

    post_save.disconnect(
        sender=Attributetype, dispatch_uid='attributeapp.attributetype.post_save.ping_directories')
    post_save.disconnect(
        sender=Attributetype, dispatch_uid='attributeapp.attributetype.post_save.ping_external_urls')
