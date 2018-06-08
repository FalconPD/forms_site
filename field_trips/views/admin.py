from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.forms.models import modelformset_factory

from field_trips.utils import is_admin
from field_trips.models import FieldTrip, Chaperone, Approval
from field_trips.forms import AdminOptionsForm, AdminArchiveForm, AdminForm
from field_trips.forms import ChaperoneForm, AdminApprovalForm
from field_trips.views.constants import ITEMS_PER_PAGE, DISPLAYS, FORMS

@login_required
def admin_index(request):
    """
    Make sure the user is an admin and then present them with an administrative
    overview
    """
    if not is_admin(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        #FIXME: Unimplemented
        form = CreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('field_trips:admin_index')
    else:
        form = AdminOptionsForm()
        archive_form = AdminArchiveForm()
        active_requests = FieldTrip.objects.filter(
            status=FieldTrip.IN_PROGRESS).all()
        return render(request, 'field_trips/admin/index.html', {
            'form': form,
            'archive_form': archive_form,
            'FieldTrip': FieldTrip,
        })

def admin_archive(request):
    return HttpResponse("Work in Progress")

def admin_board_report(request):
    return HttpResponse("Work in Progress")

@login_required
def admin_detail(request, pk):
    """
    Make sure the user is an admin and then present them with the admin form
    for editing basically all parts of a field trip
    """
    if not is_admin(request.user):
        raise PermissionDenied

    field_trip = get_object_or_404(FieldTrip, pk=pk)
    title = "Editing Field Trip #{}".format(pk)
    cards = (
        ("General Information", FORMS + 'general.html'),
        ("Transportation", FORMS + 'transportation.html'),
        ("Funding", FORMS + 'funding.html'),
        ("Curriculum", FORMS + 'curriculum.html'),
        ("Nurse", FORMS + 'nurse.html'),
        ("Approvals", FORMS + 'approvals.html'),
        ("Internals", FORMS + 'internals.html'),
    )
    form = AdminForm(instance=field_trip)
    ChaperoneFormFactory = modelformset_factory(Chaperone, form=ChaperoneForm,
        extra=0)
    chaperones = ChaperoneFormFactory(prefix='chaperones',
        queryset=Chaperone.objects.filter(field_trip=field_trip))
    ApprovalFormFactory = modelformset_factory(Approval, form=AdminApprovalForm,
        extra=0, )
    approvals = ApprovalFormFactory(prefix='approvals',
        queryset=Approval.objects.filter(field_trip=field_trip))
    return render(request, 'field_trips/show_cards.html', {
        'cards': cards,
        'field_trip': field_trip,
        'title': title,
        'form': form,
        'chaperones': chaperones,
        'approvals': approvals,
    })

@login_required
def admin_list(request, status):
    """
    Make sure the user is an admin and then list field trips based on status
    """
    if not is_admin(request.user):
        raise PermissionDenied

    order_by = request.GET.get('order_by', 'id')
    field_trips_list = (FieldTrip.objects
        .filter(status=status)
        .order_by(order_by)
        .all()
    )
    paginator = Paginator(field_trips_list, ITEMS_PER_PAGE)
    page = request.GET.get('page')
    field_trips = paginator.get_page(page)
    title = FieldTrip.lookup_status(status) + " Field Trip Requests"
    return render(request, 'field_trips/admin/list.html', {
        'field_trips': field_trips,
        'FieldTrip': FieldTrip,
        'title': title,
        'fields': ['id', 'destination', 'departing', 'submitted', 'submitter'],
    }) 
