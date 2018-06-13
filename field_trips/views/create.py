from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.forms.models import inlineformset_factory
from django.urls import reverse

from field_trips.forms import CreateForm, ChaperoneForm
from field_trips.models import FieldTrip, Chaperone, AdminOption
from .constants import FORMS

@login_required
def create(request):
    """
    Creates a view that allows ANY logged in user to submit a field trip request
    but checks to make sure the admin is accepting requests first.
    """
    admin_option = AdminOption.objects.get()
    if not admin_option.window_open:
        return HttpResponse("New field trip requests have been disabled.")

    title = "Submit a Field Trip Request"
    cards = (
        ("General Information", FORMS + 'general.html'),
        ("Transportation", FORMS + 'transportation.html'),
        ("Funding", FORMS + 'funding.html'),
        ("Curriculum", FORMS + 'curriculum.html'),
    )
    ChaperoneFormSet = inlineformset_factory(FieldTrip, Chaperone, extra=1,
        form=ChaperoneForm)
    if request.method == 'POST':
        field_trip = FieldTrip(submitter=request.user)
        form = CreateForm(request.POST, request.FILES, instance=field_trip)
        chaperones = ChaperoneFormSet(request.POST, instance=field_trip)
        if form.is_valid() and chaperones.is_valid():
            form.save()
            chaperones.save()
            return redirect('field_trips:index')
    else:
        chaperones = ChaperoneFormSet()
        form = CreateForm()
    return render(request, 'field_trips/show_cards.html', {
        'title': title,
        'cards': cards,
        'form': form,
        'chaperones': chaperones,
        'enctype': "multipart/form-data",
        'action': reverse('field_trips:create'),
        'admin_option': admin_option,
    })
