from django.shortcuts import render
from django.forms import formset_factory

from .forms import CreateForm, ChaperoneForm

def create(request):
    FormSet = formset_factory(ChaperoneForm, extra=1)
    formset = FormSet()
    form = CreateForm()
    return render(request, 'field_trips/create.html', {'form': form, 'formset': formset})
