"""Signal handlers of Objectapp"""
import inspect
from functools import wraps

from django.db.models.signals import post_save

from objectapp import settings


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
    """Ping Directories when an gbobject is saved"""
    gbobject = kwargs['instance']

    if gbobject.is_visible and settings.SAVE_PING_DIRECTORIES:
        from objectapp.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [gbobject])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """Ping Externals URLS when an gbobject is saved"""
    gbobject = kwargs['instance']

    if gbobject.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from objectapp.ping import ExternalUrlsPinger

        ExternalUrlsPinger(gbobject)


def disconnect_objectapp_signals():
    """Disconnect all the signals provided by Objectapp"""
    from objectapp.models import Gbobject

    post_save.disconnect(
        sender=Gbobject, dispatch_uid='objectapp.gbobject.post_save.ping_directories')
    post_save.disconnect(
        sender=Gbobject, dispatch_uid='objectapp.gbobject.post_save.ping_external_urls')
