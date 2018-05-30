from calendar import month_name

from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models.functions import Lower
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone

from .forms import CreateForm, ChaperoneForm, NurseForm, ApprovalForm
from .forms import PrincipalForm, SupervisorForm, AssistantSuperintendentForm
from .forms import FacilitiesForm
from .models import FieldTrip, Chaperone, Approver

DISPLAYS = 'field_trips/displays/'
FORMS = 'field_trips/forms/'

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
        'NURSE': (
            "Nurse Approval",
            [
                ("Directions", directions_dir +'nurse.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Nurse", FORMS + 'nurse.html'),
            ],
            NurseForm,
        ),
        'PRINCIPAL': (
            "Principal Approval",
            [
                ("Directions", directions_dir + 'principal.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Funding", FORMS + 'funding.html'),
            ],
            PrincipalForm,
        ),
        'SUPERVISOR': (
            "Supervisor Approval",
            [
                ("Directions", directions_dir + 'supervisor.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Curriculum", FORMS + 'curriculum.html'),
            ],
            SupervisorForm,
        ),
        'ASSISTANT SUPERINTENDENT': (
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
        'FACILITIES': (
            "Facilities Approval",
            [
                ("Directions", directions_dir + 'facilities.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Transportation", FORMS + 'transportation.html'),
            ],
            FacilitiesForm,
        ),
        'PPS': (
            "Pupil Personnel Services",
            [
                ("Directions", directions_dir + 'pps.html'),
                ("General Information", DISPLAYS + 'general.html'),
                ("Nurse", FORMS + 'nurse.html'),
            ],
            NurseForm,
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
    
@login_required
def create(request):
    """
    Creates a view that allows ANY logged in user to submit a field trip request
    """
    title = "Submit a Field Trip Request"
    cards = (
        ("General Information", FORMS + 'general.html'),
        ("Transportation", FORMS + 'transportation.html'),
        ("Funding", FORMS + 'funding.html'),
        ("Curriculum", FORMS + 'curriculum.html'),
    )
    ChaperoneFormFactory = modelformset_factory(Chaperone, form=ChaperoneForm,
        extra=1)
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        formset = ChaperoneFormFactory(request.POST)
        if form.is_valid() and formset.is_valid():
            # Create the field trip and save the submitter
            field_trip = form.save(commit=False) 
            field_trip.submitter = request.user
            field_trip.save()
            form.save_m2m() # needed due to commit=False
            # Save all the chaperones (has to be done AFTER the field trip)
            chaperone_set = formset.save(commit=False)
            for chaperone in chaperone_set:
                chaperone.field_trip = field_trip
                chaperone.save()
            return redirect('field_trips:index')
    else:
        formset = ChaperoneFormFactory(queryset=Chaperone.objects.none())
        form = CreateForm()
    return render(request, 'field_trips/show_cards.html', {'title': title,
        'cards': cards, 'form': form, 'formset': formset,
        'enctype': "multipart/form-data",
        'action': reverse('field_trips:create')})

@login_required
def index(request):
    order_by = request.GET.get('order_by', 'id')
    field_trips = (FieldTrip
        .objects
        .filter(submitter = request.user)
        .order_by(Lower(order_by)))
    return render(request, 'field_trips/index.html',
        {'field_trips': field_trips})

@login_required
def calendar(request):
    month = 5
    year = 2018
    title = "{} {}".format(month_name[month], year)
    return render(request, 'field_trips/calendar.html', {
        'title': title,
        'field_trips': None,
        'month': month,
        'year': year,
    })

@login_required
def detail(request, pk):
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    title = "Field Trip #{}".format(pk)
    cards = (
        ("General Information", DISPLAYS + 'general.html'),
        ("Transportation", DISPLAYS + 'transportation.html'),
        ("Funding", DISPLAYS + 'funding.html'),
        ("Curriculum", DISPLAYS + 'curriculum.html'),
        ("Nurse", DISPLAYS + 'nurse.html'),
        ("Approvals", DISPLAYS + 'approvals.html'),
    )
    return render(request, 'field_trips/show_cards.html', {'cards': cards,
        'field_trip': field_trip, 'title': title })
