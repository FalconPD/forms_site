from django.shortcuts import render, get_object_or_404
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .forms import CreateForm, ChaperoneForm
from .models import FieldTrip, Chaperone

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
            return HttpResponseRedirect('')
    else:
        formset = ChaperoneFormFactory()
        form = CreateForm()
    return render(request, 'field_trips/create/create.html', {'form': form, 'formset': formset})

@login_required
def detail(request, pk):
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    return render(request,'field_trips/details/details.html',
        {'field_trip': field_trip})
