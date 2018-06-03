from field_trips.models import Approver, Role

def is_approver(user):
    return Approver.objects.filter(email__iexact=user.email).exists()

def is_admin(user):
    admin_roles = (Role.objects
        .filter(code__in=(Role.FIELD_TRIP_SECRETARY,
            Role.ASSISTANT_SUPERINTENDENT))
    )
    return (Approver.objects
        .filter(email__iexact=user.email)
        .filter(roles__in=admin_roles)
        .exists()
    )
