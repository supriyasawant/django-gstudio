"""Context Processors for Gstudio"""
from gstudio import __version__


def version(request):
    """Adds version of Gstudio to the context"""
    return {'GSTUDIO_VERSION': __version__}
