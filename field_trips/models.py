from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Building(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)

    def __str__(self):
        return self.name

class FieldTrip(models.Model):
    # General Info
    email = models.EmailField("Submitter", null=True)
    destination = models.CharField(max_length=64)
    grades = models.ManyToManyField(Grade)
    group = models.CharField("Class / Group / Club", max_length=64)
    roster = models.FileField()
    itinerary = models.TextField(help_text=
        ("Please include time at destination, lunch arrangements, and "
         "additional stops."))
    pupils = models.IntegerField("Number of Pupils")
    teachers = models.IntegerField("Number of Teachers")
    departing = models.DateTimeField("Date and Time of Departure")
    returning = models.DateTimeField("Date and Time Returning to School")

    # Transportation
    directions = models.FileField()
    buses = models.IntegerField()
    extra_vehicles = models.ManyToManyField(Vehicle, verbose_name="Additional Vehicles Required")
    transported_by = models.CharField(max_length=64)
    transportation_comments = models.TextField()

    # Funding
    BUILDING_BUDGET = 'BUILDING'
    STUDENT_FUNDED = 'STUDENT'
    SOURCE_OF_FUNDS_CHOICES = (
        (BUILDING_BUDGET, 'Building Budget'),
        (STUDENT_FUNDED, 'Student Funded'),
    )
    costs = models.TextField(help_text=
        "Please describe all costs in detail. Buses are $75 per hour.")
    funds = models.CharField("Source of Funds", max_length=8, choices=SOURCE_OF_FUNDS_CHOICES)

    # Curricular Tie Ins
    standards = models.TextField("Unit(s) of Study / Curriculum Standards Addressed During Trip",
        help_text="Please be specific.")
    anticipatory = models.TextField("Description of Anticipatory Activity",
        help_text="To be completed with students in advance of trip")
    purpose = models.TextField("Description of Educational Value of Trip",
        help_text="What will the students learn, and HOW?")

    # Nurse
    nurse_required = models.NullBooleanField()
    nurse_comments = models.TextField()
    nurse_name = models.CharField(max_length=64)

    def __str__(self):
        return self.destination

class Chaperone(models.Model):
    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Approval(models.Model):
    step = models.IntegerField()
    ROLE_CHOICES = (
        ('NURSE', 'Nurse'),
        ('PRINCIPAL', 'Principal'),
        ('SUPERVISOR', 'Supervisor'),
        ('ASSISTANT SUPERINTENDANT', 'Assistant Superintendant'),
        ('BUILDINGS/GROUNDS', 'Buildings and Grounds'),
        ('TRANSPORATION', 'Transportation Secretary'),
        ('PPS', 'Pupil Personnel Services'),
        ('FIELD TRIP SECRETARY', 'Field Trip Secretary'),
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    email = models.EmailField(null=True)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)

    def __str__(self):
        return self.email
