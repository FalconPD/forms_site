from django.shortcuts import render, get_object_or_404
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .forms import CreateForm, ChaperoneForm
from .models import FieldTrip

@login_required
def create(request):
    ChaperoneFormFactory = formset_factory(ChaperoneForm, extra=1)
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        formset = ChaperoneFormFactory(request.POST)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return HttpResponseRedirect('/thanks/')
    else:
        formset = ChaperoneFormFactory()
        form = CreateForm()
    return render(request, 'field_trips/create.html', {'form': form, 'formset': formset})

@login_required
def detail(request, pk):
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    return render(request,'field_trips/details.html', {'field_trip': field_trip,
        'fields': ('destination', 'departing')})
