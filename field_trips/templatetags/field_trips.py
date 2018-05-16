from django import template
from field_trips.models import Approver

register = template.Library()

@register.filter
def is_approver(user):
    return Approver.objects.filter(email__iexact=user.email).exists()
