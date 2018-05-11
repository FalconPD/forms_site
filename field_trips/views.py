from django.shortcuts import render
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .forms import CreateForm, ChaperoneForm

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
