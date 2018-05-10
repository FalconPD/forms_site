from django import forms

from .models import FieldTrip, Chaperone, Approver

DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"

class FieldTripForm(forms.ModelForm):

    # Our date format is different, so we have to override these to specify it
    departing = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,)
    )
    returning = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,)
    )

    class Meta:
        model = FieldTrip
        fields = [] # default to nothing showing


# This is the form someone sees when they create a new field trip request
class CreateForm(FieldTripForm):

    class Meta(FieldTripForm.Meta):
        fields = ['destination', 'group', 'grades', 'roster', 'itinerary',
            'pupils', 'teachers', 'departing', 'returning', 'directions',
            'buses', 'extra_vehicles', 'costs', 'funds', 'anticipatory',
            'purpose', 'standards', 'building', 'supervisor']

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['supervisor'].queryset = Approver.objects.filter(roles__code='SUPERVISOR')

class ChaperoneForm(forms.ModelForm):

    class Meta:
        model = Chaperone
        exclude = ['field_trip']
