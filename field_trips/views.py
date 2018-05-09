from django.shortcuts import render
from django.forms import formset_factory

from .forms import CreateForm, ChaperoneForm

def create(request):
    FormSet = formset_factory(ChaperoneForm, extra=1)
    if request.method == 'POST':
        form = CreateForm(request.POST)
        formset = FormSet(request.POST)
        print(form)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        formset = FormSet()
        form = CreateForm()
    return render(request, 'field_trips/create.html', {'form': form, 'formset': formset})
