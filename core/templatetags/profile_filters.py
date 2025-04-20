from django import template

register = template.Library()

@register.filter
def getattr_attr(obj, attr_name):
    """Returns the value of the given attribute name of an object."""
    return getattr(obj, attr_name, None)
