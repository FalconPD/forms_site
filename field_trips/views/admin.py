import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.core import serializers

from field_trips.utils import is_admin
from field_trips.models import FieldTrip, Chaperone, Approval, AdminOption
from field_trips.forms import AdminOptionForm, AdminArchiveForm, AdminForm
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

    admin_options = AdminOption.objects.get()
    if request.method == 'POST':
        form = AdminOptionForm(request.POST, instance=admin_options)
        if form.is_valid():
            form.save()
            return redirect('field_trips:admin_index')
    else:
        form = AdminOptionForm(instance=admin_options)
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
    An admin view of ONE particular field trip. Allows the admin to edit
    everything (within reason) and displays some internal model features as
    well
    """
    if not is_admin(request.user):
        raise PermissionDenied

    field_trip = get_object_or_404(FieldTrip, pk=pk)
    admin_option = AdminOption.objects.get()
    other_trips = (FieldTrip
        .objects
        .filter(status__in=(FieldTrip.APPROVED, FieldTrip.IN_PROGRESS))
        .all()
    )
    other_dates = serializers.serialize('json', other_trips, fields='departing')

    ChaperoneFormSet = inlineformset_factory(FieldTrip, Chaperone, extra=0,
        form=ChaperoneForm)
    ApprovalFormSet = inlineformset_factory(FieldTrip, Approval, extra=0,
        form=AdminApprovalForm)

    if request.method == 'POST':
        form = AdminForm(request.POST, request.FILES, instance=field_trip)
        chaperones = ChaperoneFormSet(request.POST, instance=field_trip)
        approvals = ApprovalFormSet(request.POST, instance=field_trip)
        if form.is_valid() and chaperones.is_valid() and approvals.is_valid():
            form.save()
            chaperones.save()
            approvals.save()
            return redirect('field_trips:admin_index')
    else:
        form = AdminForm(instance=field_trip)
        chaperones = ChaperoneFormSet(instance=field_trip)
        approvals = ApprovalFormSet(instance=field_trip)
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
    return render(request, 'field_trips/show_cards.html', {
        'cards': cards,
        'field_trip': field_trip,
        'title': title,
        'form': form,
        'chaperones': chaperones,
        'approvals': approvals,
        'enctype': "multipart/form-data",
        'action': reverse('field_trips:admin_detail', args=[pk]),
        'admin_option': admin_option,
        'other_dates': other_dates,
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
