from django import forms

from .models import FieldTrip, Chaperone

class FieldTripForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        fields = [] # default to nothing showing
        widgets = {
                'destination': forms.TextInput(attrs={'class': 'form-control'}),
                'group': forms.TextInput(attrs={'class': 'form-control'}),
                'grades': forms.SelectMultiple(attrs={'class': 'form-control'}),
                'roster': forms.FileInput(attrs={'class': 'form-control'}),
                'itinerary': forms.Textarea(attrs={'class': 'form-control'}),
                'pupils': forms.NumberInput(attrs={'class': 'form-control'}),
                'teachers': forms.NumberInput(attrs={'class': 'form-control'}),
                'departing': forms.DateTimeInput(attrs={'class': 'form-control'}),
                'returning': forms.DateTimeInput(attrs={'class': 'form-control'}),
                'directions': forms.FileInput(attrs={'class': 'form-control'}),
                'buses': forms.NumberInput(attrs={'class': 'form-control'}),
                'extra_vehicles': forms.SelectMultiple(attrs={'class': 'form-control'}),
                'transported_by': forms.TextInput(attrs={'class': 'form-control'}),
                'transportation_comments': forms.Textarea(attrs={'class': 'form-control'}),
                'costs': forms.Textarea(attrs={'class': 'form-control'}),
                'funds': forms.Select(attrs={'class': 'form-control'}),
                'anticipatory': forms.Textarea(attrs={'class': 'form-control'}),
                'purpose': forms.Textarea(attrs={'class': 'form-control'}),
                'standards': forms.Textarea(attrs={'class': 'form-control'}),
        }

# This is the form someone sees when they create a new field trip request
class CreateForm(FieldTripForm):

    class Meta(FieldTripForm.Meta):
        fields = ['destination', 'group', 'grades', 'roster', 'itinerary',
            'pupils', 'teachers', 'departing', 'returning', 'directions',
            'buses', 'extra_vehicles', 'costs', 'funds', 'anticipatory',
            'purpose', 'standards']

class ChaperoneForm(forms.ModelForm):

    class Meta:
        model = Chaperone
        exclude = ['field_trip']
        widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
