"""Signal handlers of Relationapp"""
import inspect
from functools import wraps

from django.db.models.signals import post_save

from relationapp import settings


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
    """Ping Directories when an relationtype is saved"""
    relationtype = kwargs['instance']

    if relationtype.is_visible and settings.SAVE_PING_DIRECTORIES:
        from relationapp.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [relationtype])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """Ping Externals URLS when an relationtype is saved"""
    relationtype = kwargs['instance']

    if relationtype.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from relationapp.ping import ExternalUrlsPinger

        ExternalUrlsPinger(relationtype)


def disconnect_relationapp_signals():
    """Disconnect all the signals provided by Relationapp"""
    from relationapp.models import Relationtype

    post_save.disconnect(
        sender=Relationtype, dispatch_uid='relationapp.relationtype.post_save.ping_directories')
    post_save.disconnect(
        sender=Relationtype, dispatch_uid='relationapp.relationtype.post_save.ping_external_urls')
