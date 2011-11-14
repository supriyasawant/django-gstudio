"""Context Processors for Relationapp"""
from relationapp import __version__


def version(request):
    """Adds version of Relationapp to the context"""
    return {'RELATIONAPP_VERSION': __version__}
