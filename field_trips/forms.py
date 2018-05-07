from django import forms

from .models import FieldTrip

class CreateForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        exclude = ['email', 'transported_by', 'transportation_comments',
            'nurse_required', 'nurse_comments', 'nurse_name']
