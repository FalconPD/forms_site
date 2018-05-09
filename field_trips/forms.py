from django import forms

from .models import FieldTrip, Chaperone, Approver

class FieldTripForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        fields = [] # default to nothing showing
        widgets = {
            'departing': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
            'returning': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
        }

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
