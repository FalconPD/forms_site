from django import forms

from .models import FieldTrip, Chaperone, Approver, Approval

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

class CreateForm(FieldTripForm):
    """
    This is the form someone sees when they create a new field trip request.
    It hides some fields and correctly populates the supervisor list
    """

    class Meta(FieldTripForm.Meta):
        fields = ['destination', 'group', 'grades', 'roster', 'itinerary',
            'pupils', 'teachers', 'departing', 'returning', 'directions',
            'buses', 'extra_vehicles', 'costs', 'funds', 'anticipatory',
            'purpose', 'standards', 'building', 'supervisor']

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['supervisor'].queryset = Approver.objects.filter(roles__code='SUPERVISOR')

class NurseForm(FieldTripForm):
    """
    This is the form a nurse sees when they got to approve a field trip request.
    They can only edit things in the nurse section.
    
    """

    class Meta(FieldTripForm.Meta):
        fields = ['nurse_required', 'nurse_comments', 'nurse_name']

class ApprovalForm(forms.ModelForm):

    class Meta:
        model = Approval
        fields = ['approved', 'comments']

class ChaperoneForm(forms.ModelForm):

    class Meta:
        model = Chaperone
        exclude = ['field_trip']
