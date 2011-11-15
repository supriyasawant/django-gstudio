"""Context Processors for Attributeapp"""
from attributeapp import __version__


def version(request):
    """Adds version of Attributeapp to the context"""
    return {'ATTRIBUTEAPP_VERSION': __version__}
