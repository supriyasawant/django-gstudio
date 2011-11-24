# a sample module for generating dynamic forms
from gstudio.models import Attributetype

def inputitems():
    """collect all the input fields and return a form in xml"""
    items = []
    for each in Attributetype.objects.all():
        items.append(each.inputform_xml())
    inputitems = ''
    for each in items:
        inputitems += each
    return inputitems
        

def formmodel():

    """ return the header for the xform """
    for each in Attributetype.objects.all():
        return each.simpleform_xml()

def fullform():
    """ compose to produce the final form"""
    head = formmodel()
    xml = head + inputitems() + "</form> </xform>"
    return xml
               
    
