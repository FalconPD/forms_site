from django import forms

from .models import FieldTrip, Chaperone, Approver, Approval

DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"

class FieldTripForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        fields = [] # default to nothing showing

class CreateForm(FieldTripForm):
    """
    This is the form someone sees when they create a new field trip request.
    It hides some fields and correctly populates the supervisor list
    """

    # Our date format in the picker is different, so we have to override these
    # to specify it
    departing = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,)
    )
    returning = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,)
    )

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
    This is the form a nurse sees when they go to approve a field trip request.
    They can only edit things in the nurse section.
    
    """
    class Meta(FieldTripForm.Meta):
        fields = ['nurse_required', 'nurse_comments', 'nurse_name']

    # This forces the nurse to select Yes or No
    def clean_nurse_required(self):
        data = self.cleaned_data['nurse_required']
        if data == None:
            raise forms.ValidationError("Please select Yes or No")

        return data 

class PrincipalForm(FieldTripForm):
    """
    This is the form a principal sees when they go to approve a field trip
    request. They are primarily in charge of overseeing costs and have the
    ability to adjust them here
    """
    class Meta(FieldTripForm.Meta):
        fields = ['costs', 'funds']

class SupervisorForm(FieldTripForm):
    """
    This is the form a supervisor sees when they go to approve a field trip
    request. They have the ability to adjust the curriculum questions.
    """
    class Meta(FieldTripForm.Meta):
        fields = ['anticipatory', 'purpose', 'standards']

class AssistantSuperintendentForm(FieldTripForm):
    """
    This is the form the assitant superintendent sees when they go to approve
    a field trip request. They have the ability to adjust the funding and
    curriculum sections.
    """
    class Meta(FieldTripForm.Meta):
        fields = ['costs', 'funds', 'anticipatory', 'purpose', 'standards']

class FacilitiesForm(FieldTripForm):
    """
    This is the form facilities sees when a field trip request specifies extra
    vehicles. They have the ability to adjust the transportation section
    """
    class Meta(FieldTripForm.Meta):
        fields = ['directions', 'buses', 'extra_vehicles', 'transported_by',
            'transportation_comments']

class ApprovalForm(forms.ModelForm):
    """
    This is what an approver sees when they have to approve something.
    """
    class Meta:
        model = Approval
        fields = ['approved', 'comments']

    # This forces the approvers to select Yes or No
    def clean_approved(self):
        data = self.cleaned_data['approved']
        if data == None:
            raise forms.ValidationError("Please select Yes or No")

        return data

class ChaperoneForm(forms.ModelForm):

    class Meta:
        model = Chaperone
        exclude = ['field_trip']
