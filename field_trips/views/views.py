from calendar import month_name

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.utils import timezone
from django.urls import reverse

from field_trips.models import FieldTrip

@login_required
def index(request):
    order_by = request.GET.get('order_by', 'id')
    field_trips = (FieldTrip
        .objects
        .filter(submitter = request.user)
        .order_by(Lower(order_by)))
    return render(request, 'field_trips/index.html',
        {'field_trips': field_trips})

def calendar_link(month, year):
    return '{}?month={}&year={}'.format(reverse('field_trips:calendar'), month,
        year)

def calendar_title(month, year):
    return '{} {}'.format(month_name[month], year)

@login_required
def calendar(request):
    now = timezone.now()
    month = int(request.GET.get('month', str(now.month)))
    year = int(request.GET.get('year', str(now.year)))
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year
    title = calendar_title(month, year)
    previous_link = calendar_link(previous_month, previous_year)
    previous_title = calendar_title(previous_month, previous_year)
    next_link = calendar_link(next_month, next_year)
    next_title = calendar_title(next_month, next_year)
    return render(request, 'field_trips/calendar.html', {
        'title': title,
        'field_trips': None,
        'month': month,
        'year': year,
        'previous_link': previous_link,
        'previous_title': previous_title,
        'next_link': next_link,
        'next_title': next_title,
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
