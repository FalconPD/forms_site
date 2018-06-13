from calendar import month_name

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator

from field_trips.models import FieldTrip
from .constants import DISPLAYS, ITEMS_PER_PAGE

@login_required
def index(request):
    field_trips = FieldTrip.objects.filter(submitter=request.user)
    status_text_count = []
    for status, text in FieldTrip.STATUS_CHOICES:
        count = field_trips.filter(status=status).count()
        if count != 0:
            status_text_count.append((status, text, count))
    return render(request, 'field_trips/index.html', {
        'status_text_count': status_text_count,
    })

@login_required
def list(request, status):
    order_by = request.GET.get('order_by', 'id')
    field_trips_list = (FieldTrip
        .objects
        .filter(submitter = request.user)
        .filter(status = status)
        .order_by(order_by)
        .all()
    )
    paginator = Paginator(field_trips_list, ITEMS_PER_PAGE)
    page = request.GET.get('page')
    field_trips = paginator.get_page(page)
    title = "My {} Field Trips".format(FieldTrip.lookup_status(status))
    return render(request, 'field_trips/list.html', {
        'title': title,
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
        .filter(status__in=[FieldTrip.IN_PROGRESS, FieldTrip.APPROVED,
            FieldTrip.PENDING])
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
