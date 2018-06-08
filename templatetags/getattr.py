from django import template
register = template.Library()

@register.filter
def getattr(obj, attribute):
    return obj.__getattribute__(attribute)
