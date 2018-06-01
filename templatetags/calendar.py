# Based On: https://djangosnippets.org/snippets/1485/

from django import template
from calendar import Calendar, month_name
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

    def link(self, year, month):
        """
        Create a calendar link with query parameters for a specific year and
        month
        """
        return '{}?year={}&month={}'.format('', year, month)

    def title(self, year, month):
        """
        Create a friendly title for a month and year
        """
        return '{} {}'.format(month_name[month], year)

    def next_year_month(self):
        """
        Find the next month, increment year if needed
        """
        if self.month_val == 12:
            next_year = self.year_val + 1
            next_month = 1
        else:
            next_year = self.year_val
            next_month = self.month_val + 1
        return (next_year, next_month)

    def previous_year_month(self):
        """
        Find the previous month, decerement year if needed
        """
        if self.month_val == 1:
            previous_year = self.year_val - 1
            previous_month = 12
        else:
            previous_year = self.year_val
            previous_month = self.month_val - 1
        return (previous_year, previous_month)

    def render(self, context):
        """
        Create an object in the context with links and a calendar
        """
        self.year_val = int(self.year.resolve(context))
        self.month_val = int(self.month.resolve(context))
        full_cal = Calendar(6).monthdatescalendar(self.year_val, self.month_val)
        # We only want to see days in our month
        sparse_cal = []
        for week in full_cal:
            new_week = []
            for day in week:
                if day.month == self.month_val:
                    new_week.append(day)
                else:
                    new_week.append(None)
            sparse_cal.append(new_week)
        context[self.var_name] = {
            'calendar': sparse_cal,
            'title': self.title(self.year_val, self.month_val), 
            'next_link': self.link(*self.next_year_month()),
            'next_title': self.title(*self.next_year_month()),
            'previous_link': self.link(*self.previous_year_month()),
            'previous_title': self.title(*self.previous_year_month()),
        }
        return ''
