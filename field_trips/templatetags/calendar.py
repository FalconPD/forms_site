# https://djangosnippets.org/snippets/1485/
# This tag gives you an iterable Python Calendar object in your template
# namespace. It is used in the django-calendar project.

from django import template
from calendar import Calendar
import datetime
import re
   
register = template.Library()
    
@register.tag(name="get_calendar")
def do_calendar(parser, token):
    syntax_help = "syntax should be \"get_calendar for <month> <year> as <var_name>\""
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        error = "{} tag requires arguments, {}".format(
            token.contents.split()[0], syntax_help)
        raise template.TemplateSyntaxError(error)
    m = re.search(r'for (.*?) (.*?) as (\w+)', arg)
    if not m:
        error = "{} tag had invalid arguments, {}".format(tag_name, syntax_help)
        raise template.TemplateSyntaxError(error)
    return GetCalendarNode(*m.groups())
                                                                     
class GetCalendarNode(template.Node):
    def __init__(self, month, year, var_name):
        self.year = template.Variable(year)
        self.month = template.Variable(month)
        self.var_name = var_name

    def render(self, context):
        mycal = Calendar(6)
        context[self.var_name] = mycal.monthdatescalendar(
            int(self.year.resolve(context)), int(self.month.resolve(context)))
        return ''
