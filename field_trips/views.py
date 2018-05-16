from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models.functions import Lower
from django.core.exceptions import PermissionDenied

from .forms import CreateForm, ChaperoneForm
from .models import FieldTrip, Chaperone, Approver

@login_required
def approve(request):
    if not Approver.objects.filter(email__iexact=request.user.email).exists():
        raise PermissionDenied
    return HttpResponse("You've made it to the approval page.")
    
@login_required
def create(request):
    ChaperoneFormFactory = modelformset_factory(Chaperone, form=ChaperoneForm,
        extra=1)
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        formset = ChaperoneFormFactory(request.POST)
        if form.is_valid() and formset.is_valid():
            field_trip = form.save(commit=False) 
            field_trip.submitter = request.user
            field_trip.save()
            chaperone_set = formset.save(commit=False)
            for chaperone in chaperone_set:
                chaperone.field_trip = field_trip
                chaperone.save()
            field_trip.process_approvals()
            return redirect('field_trips:index')
    else:
        formset = ChaperoneFormFactory(queryset=Chaperone.objects.none())
        form = CreateForm()
    return render(request, 'field_trips/create/create.html',
        {'form': form, 'formset': formset})

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
    return HttpResponse("Not yet implemented")

@login_required
def detail(request, pk):
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    return render(request, 'field_trips/details/details.html',
        {'field_trip': field_trip})
