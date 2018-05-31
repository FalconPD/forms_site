from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms.models import modelformset_factory
from django.urls import reverse

from field_trips.forms import CreateForm, ChaperoneForm, Chaperone

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
