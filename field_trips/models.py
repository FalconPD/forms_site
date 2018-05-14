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

class Role(models.Model):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Approver(models.Model):
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    email = models.EmailField()
    roles = models.ManyToManyField(Role)

    class Meta:
        ordering = ['name']

    def __str__(self):
        buildings = ", ".join(map(str, self.building_set.all()))
        if len(buildings) > 0:
            return '{}: {}, {}'.format(self.name, self.title, buildings)
        else:
            return '{}: {}'.format(self.name, self.title) 

class Building(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)
    approvers = models.ManyToManyField(Approver)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class FieldTrip(models.Model):
    # General Info
    email = models.EmailField("Submitter")
    submitted = models.DateTimeField("Submitted")
    destination = models.CharField(max_length=64)
    group = models.CharField("Class / Group / Club", max_length=64)
    grades = models.ManyToManyField(Grade)
    building = models.OneToOneField(Building, on_delete=models.CASCADE)
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
    buses = models.IntegerField("Number of Buses Required", help_text="Each bus seats 52 people.")
    extra_vehicles = models.ManyToManyField(Vehicle, blank=True,
        verbose_name="Additional Vehicles Required")
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
    supervisor = models.OneToOneField(Approver, on_delete=models.CASCADE,
        verbose_name="Approving Supervisor")
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

#class Approval(models.Model):
#    step = models.IntegerField()
#    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
#    email = models.EmailField(null=True)
#    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
#
#    def __str__(self):
#        return self.email
