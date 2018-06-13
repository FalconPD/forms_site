from django import template
from django.utils.safestring import mark_safe
from field_trips.utils import is_approver as utils_is_approver
from field_trips.utils import is_admin as utils_is_admin
from field_trips.models import FieldTrip

register = template.Library()

@register.filter
def is_approver(user):
    return utils_is_approver(user)     

@register.filter
def is_admin(user):
    return utils_is_admin(user)

@register.simple_tag
def field_trip_dates():
    """
    Returns a list of field trip departure dates in JSON format for any
    IN_PROGRESS, APPROVED, or PENDING field trips. This is used with javascript
    to give a warning if someone is submitting a field trip on a day when there
    are other field trips
    """
    field_trips = (FieldTrip
        .objects
        .filter(status__in=(FieldTrip.IN_PROGRESS, FieldTrip.APPROVED,
            FieldTrip.PENDING))
        .all()
    )
    dates = [ "'{}'".format(field_trip.departing.isoformat()) for field_trip in field_trips ]
    dates_json = mark_safe("[{}]".format(",".join(dates)))
    return dates_json
