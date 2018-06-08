from calendar import month_name

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.utils import timezone
from django.urls import reverse

from field_trips.models import FieldTrip
from .constants import DISPLAYS

@login_required
def index(request):
    order_by = request.GET.get('order_by', 'id')
    field_trips = (FieldTrip
        .objects
        .filter(submitter = request.user)
        .order_by(order_by)
    )
    return render(request, 'field_trips/index.html', {
        'field_trips': field_trips,
        'fields': ['id', 'destination', 'departing', 'submitted'],
    })

@login_required
def calendar(request):
    now = timezone.now()
    month = int(request.GET.get('month', str(now.month)))
    year = int(request.GET.get('year', str(now.year)))
    field_trips = (FieldTrip
        .objects
        .filter(departing__year=year)
        .filter(departing__month=month)
    )
    events = []
    for field_trip in field_trips:
        events.append({
            'title': field_trip.destination,
            'link': reverse('field_trips:detail', args=[field_trip.id]),
            'date': field_trip.departing.date,
        })
    return render(request, 'calendar.html', {
        'title': 'Field Trips',
        'events': events,
        'month': month,
        'year': year,
    })

@login_required
def detail(request, pk):
    field_trip = get_object_or_404(FieldTrip, pk=pk)
    title = "Field Trip #{}".format(pk)
    cards = (
        ("General Information", DISPLAYS + 'general.html'),
        ("Transportation", DISPLAYS + 'transportation.html'),
        ("Funding", DISPLAYS + 'funding.html'),
        ("Curriculum", DISPLAYS + 'curriculum.html'),
        ("Nurse", DISPLAYS + 'nurse.html'),
        ("Approvals", DISPLAYS + 'approvals.html'),
    )
    return render(request, 'field_trips/show_cards.html', {'cards': cards,
        'field_trip': field_trip, 'title': title })
