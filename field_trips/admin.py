from django.contrib import admin

from .models import Chaperone, FieldTrip, Vehicle, Grade, Role, Approver, Building

class ChaperoneInline(admin.TabularInline):
    model = Chaperone
    extra = 2

class FieldTripAdmin(admin.ModelAdmin):
    readonly_fields = ('submitted',)
    fieldsets = [
        ('General Information',  {'fields': [
            'submitted',
            'submitter',
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
    inlines = [ChaperoneInline]

admin.site.register(FieldTrip, FieldTripAdmin)
admin.site.register(Vehicle)
admin.site.register(Grade)
admin.site.register(Role)
admin.site.register(Approver)
admin.site.register(Building)
admin.site.register(Chaperone)
