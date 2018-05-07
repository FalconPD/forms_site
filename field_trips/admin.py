from django.contrib import admin

from .models import Chaperone, FieldTrip, Vehicle, Grade, Approval

class ChaperoneInline(admin.TabularInline):
    model = Chaperone
    extra = 2

class ApprovalInline(admin.TabularInline):
    model = Approval
    extra = 6

class FieldTripAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General Information',  {'fields': [
            'email',
            'destination',
            'grades',
            'group',
            'roster',
            'itinerary',
            'pupils',
            'teachers',
            'departing',
            'returning',
        ]}),
        ('Transportation', {'fields': [
            'directions',
            'buses',
            'extra_vehicles',
            'transported_by',
            'transportation_comments',
        ]}),
        ('Funding', {'fields': [
            'costs',
            'funds',
        ]}),
        ('Curricular Tie Ins', {'fields': [
            'standards',
            'anticipatory',
            'purpose',
        ]}),
        ('Nurse', {'fields': [
            'nurse_required',
            'nurse_comments',
            'nurse_name',
        ]})
    ]
    inlines = [ChaperoneInline, ApprovalInline]

admin.site.register(FieldTrip, FieldTripAdmin)
admin.site.register(Vehicle)
admin.site.register(Grade)
