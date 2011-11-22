from gstudio.models import Attributetype

def inputitems():
    """collect all the input fields"""
    items = []
    for each in Attributetype.objects.all():
        items.append(each.inputform_xml())
    inputitems = ''
    for each in items:
        inputitems += each
    return inputitems
        

def formmodel():

    for each in Attributetype.objects.all():
        return each.simpleform_xml()

def fullform():
    head = formmodel()
    xml = head + inputitems() + "</form> </xform>"
    return xml
               
    
