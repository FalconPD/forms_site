from django import template
from field_trips.utils import is_approver as utils_is_approver
from field_trips.utils import is_admin as utils_is_admin

register = template.Library()

@register.filter
def is_approver(user):
    return utils_is_approver(user)     

@register.filter
def is_admin(user):
    return utils_is_admin(user)     
