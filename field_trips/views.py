from django.shortcuts import render

from .forms import CreateForm

def create(request):
    form = CreateForm()
    return render(request, 'field_trips/create.html', {'form': form})
