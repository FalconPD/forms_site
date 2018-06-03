from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from field_trips.utils import is_admin

@login_required
def admin_index(request):
    """
    Make sure the user is an admin and then present them with an administrative
    overview of the system with edit options.
    """
    if not is_admin(request.user):
        raise PermissionDenied

    return HttpResponse("Work in progress");
