import random
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile

from field_trips.models import FieldTrip, AdminOption, User, Grade, Building
from field_trips.models import Discipline, Vehicle

class Command(BaseCommand):
    help = "Creates random field trip requests within the current window"

    def random_date(self):
        """
        Generate a random datetime in our window
        """
        admin_option = AdminOption.objects.get()
        start = admin_option.window_start
        end = admin_option.window_end
        return start + datetime.timedelta(
            seconds=random.randint(0, int((end - start).total_seconds())))

    def create(self):
        """
        Makes a random request, saves it, and prints out a status message
        """
        destinations = ("Stop N Shop", "NTO Bus Tour", "DNTs",
            "Battleview Orchards", "Freehold Mall", "Etsch Farms",
            "Monroe Diner", "Holmdel Park", "Rutgers Stadium", "Barclay Brook")
        groups = ("Grade 2", "Falcon Life", "Senior Class", "Band",
            "Peace Ambasadors", "Football Program")

        submitter = User.objects.order_by('?').first()
        destination = random.choice(destinations)
        group = random.choice(groups)
        grades = Grade.objects.order_by('?')[:random.randint(1,3)]
        building = Building.objects.order_by('?').first()
        pupils = random.randint(1,116)
        teachers = int(pupils / 25)
        departing = self.random_date()
        returning = departing + datetime.timedelta(hours=random.randint(1,24))
        buses = int((pupils+teachers)/52)
        extra_vehicles = ();
        if random.random() < 0.25:
            extra_vehicles = Vehicle.objects.order_by('?')[:random.randint(1,2)]
        discipline = Discipline.objects.order_by('?').first()
        test_file = ContentFile("This is a test file.")
        roster = test_file
        directions = test_file

        field_trip = FieldTrip(
            submitter=submitter,
            destination=destination,
            group=group,
            building=building,
            pupils=pupils,
            teachers=teachers,
            departing=departing,
            returning=returning,
            buses=buses,
            discipline=discipline,
            roster=roster,
            directions=directions,
        )
        field_trip.save()
        field_trip.grades.set(grades)
        field_trip.extra_vehicles.set(extra_vehicles)
        self.stdout.write(self.style.SUCCESS("Created '{}'".format(field_trip)))

    def add_arguments(self, parser):
        parser.add_argument('num', type=int, nargs='?', default='1',
            help="how many to create")

    def handle(self, *args, **options):
        num = options['num']
        for i in range(num):
            self.create()            
