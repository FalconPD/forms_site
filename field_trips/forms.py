from django import forms
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Submit

from .models import FieldTrip

class CreateForm(forms.ModelForm):

#    def __init__(self, *args, **kwargs):
#        super(CreateForm, self).__init__(*args, **kwargs)
#        self.helper = FormHelper()
#        self.helper.form_id = 'id-create'
#        self.helper.form_class = 'createForm'
#        self.helper.form_method = 'post'
#        self.helper.form_action = 'create'
#        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = FieldTrip
        exclude = ['email', 'transported_by', 'transportation_comments',
            'nurse_required', 'nurse_comments', 'nurse_name']
