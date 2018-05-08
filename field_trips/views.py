from django.shortcuts import render
from django.forms import modelformset_factory

from .forms import CreateForm
from .models import Chaperone

def create(request):
    ChaperoneFormSet = modelformset_factory(Chaperone, fields=['name', 'phone_number'], extra=2)
    chaperone_formset = ChaperoneFormSet()
    form = CreateForm()
    return render(request, 'field_trips/create.html', {'form': form, 'chaperone_formset': chaperone_formset})
