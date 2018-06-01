from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from field_trips.forms import NurseForm, ApprovalForm, PrincipalForm
from field_trips.forms import SupervisorForm, AssistantSuperintendentForm
from field_trips.forms import FacilitiesForm, FieldTripSecretaryForm
from field_trips.models import FieldTrip, Approver, Role
from .constants import DISPLAYS, FORMS

@login_required
def approve(request, pk):
    """
    Make sure the person CAN approve this field trip and then show them the
    view that corresponds to the needed approval. If they can provide multiple
    needed approvals, this will show the FIRST approval.
    """

    # Check permissions
    approver = Approver.objects.filter(email__iexact=request.user.email).first()
    if not approver:
        raise PermissionDenied
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    approval = field_trip.first_needed_approval_for_approver(approver)
    if not approval:
        raise PermissionDenied

    directions_dir = 'field_trips/approve/directions/'
    view_setup = {
        Role.NURSE: (
            "Nurse Approval",
            [
                ("Directions", directions_dir +'nurse.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Nurse", FORMS + 'nurse.html'),
            ],
            NurseForm,
        ),
        Role.PRINCIPAL: (
            "Principal Approval",
            [
                ("Directions", directions_dir + 'principal.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Funding", FORMS + 'funding.html'),
            ],
            PrincipalForm,
        ),
        Role.SUPERVISOR: (
            "Supervisor Approval",
            [
                ("Directions", directions_dir + 'supervisor.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Curriculum", FORMS + 'curriculum.html'),
            ],
            SupervisorForm,
        ),
        Role.ASSISTANT_SUPERINTENDENT: (
            "Assistant Superintendent Approval",
            [
                ("Directions",directions_dir + 'assistant_superintendent.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Transportation", DISPLAYS + 'transportation.html'),
                ("Funding", FORMS + 'funding.html'),
                ("Curriculum", FORMS + 'curriculum.html'),
                ("Nurse", DISPLAYS + 'nurse.html'),
            ],
            AssistantSuperintendentForm,
        ),
        Role.FACILITIES: (
            "Facilities Approval",
            [
                ("Directions", directions_dir + 'facilities.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Transportation", FORMS + 'transportation.html'),
            ],
            FacilitiesForm,
        ),
        Role.PPS: (
            "Pupil Personnel Services",
            [
                ("Directions", directions_dir + 'pps.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Nurse", FORMS + 'nurse.html'),
            ],
            NurseForm,
        ),
        Role.FIELD_TRIP_SECRETARY: (
            "Field Trip Secretary",
            [
                ("Directions", directions_dir + 'field_trip_secretary.html'),
            ],
            FieldTripSecretaryForm,
        ),
    }

    if approval.role.code in view_setup:
        title, cards, ModelForm = view_setup[approval.role.code]
        title += " for Field Trip #{}".format(field_trip.id)
        cards.append(("Approvals", DISPLAYS + 'approvals.html'))
        cards.append(("Approval", FORMS + 'approval.html'))
    else:
        return HttpResponse(
            "Unable to render role for approval: {}".format(approval)
        )

    if request.method == 'POST': # check what was submitted
        form = ModelForm(request.POST, instance=field_trip)
        approval_form = ApprovalForm(request.POST, instance=approval)
        if approval_form.is_valid() and form.is_valid():
            approval = approval_form.save(commit=False)
            approval.approver = approver
            approval.save()
            field_trip.save()
            return redirect('field_trips:approve_index')
    else: # or create a new approval form
        form = ModelForm(instance=field_trip)
        approval_form = ApprovalForm(instance=approval)

    # render the approval view
    return render(
        request, 'field_trips/show_cards.html',
        {
            'field_trip': field_trip,
            'form': form,
            'title': title,
            'cards': cards,
            'action': reverse('field_trips:approve', args=[field_trip.id]),
            'approval_form': approval_form,
        }
    )

@login_required
def approve_index(request):
    """
    Make sure the person is an approver and then show them all field trips
    they could approve
    """
    approver = Approver.objects.filter(email__iexact=request.user.email).first()
    
    if not approver:
        raise PermissionDenied

    field_trips = []
    for field_trip in FieldTrip.objects.filter(status=FieldTrip.IN_PROGRESS):
        if field_trip.first_needed_approval_for_approver(approver):
            field_trips.append(field_trip)

    return render(request, 'field_trips/approve/index.html',
        {'field_trips': field_trips})
