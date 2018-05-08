from django import forms

from .models import FieldTrip, Chaperone

class CreateForm(forms.ModelForm):

    class Meta:
        model = FieldTrip
        exclude = ['email', 'transported_by', 'transportation_comments',
            'nurse_required', 'nurse_comments', 'nurse_name']
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
                'costs': forms.Textarea(attrs={'class': 'form-control'}),
                'funds': forms.Select(attrs={'class': 'form-control'}),
                'anticipatory': forms.Textarea(attrs={'class': 'form-control'}),
                'purpose': forms.Textarea(attrs={'class': 'form-control'}),
                'standards': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ChaperoneForm(forms.ModelForm):

    class Meta:
        model = Chaperone
        exclude = ['field_trip']
        widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
