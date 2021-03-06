from django import forms
from django.utils import timezone

from .models import FieldTrip, Chaperone, Approver, Approval, AdminOption

DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"

class FieldTripForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        fields = [] # default to nothing showing

class CreateForm(FieldTripForm):
    """
    This is the form someone sees when they create a new field trip request.
    It hides some fields
    """

    # Our date format in the picker is different, so we have to override these
    # to specify it
    departing = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,),
        required=False,
    )
    returning = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,),
        required=False,
    )

    class Meta(FieldTripForm.Meta):
        fields = ['destination', 'group', 'grades', 'roster', 'itinerary',
            'pupils', 'teachers', 'departing', 'returning', 'directions',
            'buses', 'extra_vehicles', 'funds', 'lodging', 'airfare', 'baggage',
            'mileage', 'tolls', 'parking', 'shuttle', 'stipend', 'registration',
            'meals', 'ticket', 'other', 'anticipatory', 'purpose', 'standards',
            'building', 'discipline']

    def clean(self):
        cleaned_data = super().clean()

        # Don't validate drafts
        if self.instance.status == FieldTrip.DRAFT:
            return

        # make sure nothing is blank
        validation_error = forms.ValidationError("This field is required")
        for field in self.Meta.fields:
            if self.cleaned_data[field] == '':
                self.add_error(field, validation_error)

        # make sure the departure is within the admin departure window
        admin_option = AdminOption.objects.get()
        departing = self.cleaned_data['departing']
        start = admin_option.window_start
        end = admin_option.window_end
        if departing > end or departing < start:
            validation_error = forms.ValidationError(
                "Departure must be between {} and {}".format(
                    timezone.localtime(start).strftime(DATETIME_FORMAT),
                    timezone.localtime(end).strftime(DATETIME_FORMAT))
            )
            self.add_error('departing', validation_error)


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
        fields = ['funds', 'lodging', 'airfare', 'baggage', 'mileage', 'tolls',
            'parking', 'shuttle', 'stipend', 'registration', 'meals', 'ticket',
            'other']

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
        fields = ['funds', 'lodging', 'airfare', 'baggage', 'mileage', 'tolls',
            'parking', 'shuttle', 'stipend', 'registration', 'meals', 'ticket',
            'other', 'anticipatory', 'purpose', 'standards']

class TransportationForm(FieldTripForm):
    """
    This is the form facilities sees when a field trip request specifies extra
    vehicles or transportation sees. They have the ability to adjust the
    transportation section
    """
    class Meta(FieldTripForm.Meta):
        fields = ['directions', 'buses', 'extra_vehicles', 'transported_by',
            'transportation_comments']

class FieldTripSecretaryForm(FieldTripForm):
    """
    This is the form the field trip secretary sees when they go to approve
    a field trip. The next step is board approval
    """
    class Meta(FieldTripForm.Meta):
        fields = []

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

class AdminForm(FieldTripForm):
    """
    This is what an admin sees when they view the details of a field trip
    from the admin interface
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
        fields = ['submitter', 'destination', 'group', 'grades', 'building',
            'roster', 'itinerary', 'pupils', 'teachers', 'departing',
            'returning', 'directions', 'buses', 'extra_vehicles',
            'transported_by', 'transportation_comments', 'funds', 'lodging',
            'airfare', 'baggage', 'mileage', 'tolls', 'parking', 'shuttle',
            'stipend', 'registration', 'meals', 'ticket', 'other', 'discipline',
            'standards', 'anticipatory', 'purpose', 'nurse_required',
            'nurse_comments', 'nurse_name', 'status']

class AdminOptionForm(forms.ModelForm):
    """
    This is what an admin sees on the top part of the admin page
    """
    window_start = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,),
        help_text="Only accept requests with a departure date AFTER this date"
    )
    window_end = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,),
        help_text="Only accept request with a departure date BEFORE this date"
    )

    class Meta:
        model = AdminOption
        fields = ['window_open', 'window_start', 'window_end']

class AdminActionForm(forms.Form):
    """
    This is part of the admin actions card
    """
    archive = forms.BooleanField()
    date = forms.DateTimeField(
        widget=forms.DateInput(format=DATETIME_FORMAT),
        input_formats=(DATETIME_FORMAT,),
        label='Requests older than',
    )

class AdminApprovalForm(forms.ModelForm):
    """
    This is what an admin sees in the card showing a list of approvals
    """
    class Meta:
        model = Approval
        fields = ['role', 'approver', 'approved', 'comments']
        widgets = {
            # take up less space in the table
            'comments': forms.Textarea(attrs={'rows': 2}),
        }

