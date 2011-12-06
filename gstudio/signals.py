"""Signal handlers of Gstudio"""
import inspect
from functools import wraps

from django.db.models.signals import post_save

from gstudio import settings


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
    """Ping Directories when an nodetype is saved"""
    nodetype = kwargs['instance']

    if nodetype.is_visible and settings.SAVE_PING_DIRECTORIES:
        from gstudio.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [nodetype])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """Ping Externals URLS when an nodetype is saved"""
    nodetype = kwargs['instance']

    if nodetype.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from gstudio.ping import ExternalUrlsPinger

        ExternalUrlsPinger(nodetype)


def disconnect_gstudio_signals():
    """Disconnect all the signals provided by Gstudio"""
    from gstudio.models import Nodetype

    post_save.disconnect(
        sender=Nodetype, dispatch_uid='gstudio.nodetype.post_save.ping_directories')
    post_save.disconnect(
        sender=Nodetype, dispatch_uid='gstudio.nodetype.post_save.ping_external_urls')
