from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

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
    email = models.EmailField()
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    roles = models.ManyToManyField(Role)

    class Meta:
        ordering = ['name']

    def __str__(self):
        buildings = ", ".join(map(str, self.building_set.all()))
        if len(buildings) > 0:
            return '{} {}, {}'.format(self.name, self.title, buildings)
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
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted = models.DateTimeField("Submitted", auto_now_add=True)
    destination = models.CharField(max_length=64)
    group = models.CharField("Class / Group / Club", max_length=64)
    grades = models.ManyToManyField(Grade)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    roster = models.FileField(upload_to="field_trips/")
    itinerary = models.TextField(help_text=
        ("Please include time at destination, lunch arrangements, and "
         "additional stops."))
    pupils = models.IntegerField("Number of Pupils")
    teachers = models.IntegerField("Number of Teachers")
    departing = models.DateTimeField("Date and Time of Departure")
    returning = models.DateTimeField("Date and Time Returning to School")

    # Transportation
    directions = models.FileField(upload_to="field_trips/")
    buses = models.IntegerField("Number of Buses Required", help_text="Each bus seats 52 people.")
    extra_vehicles = models.ManyToManyField(Vehicle, blank=True,
        verbose_name="Additional Vehicles Required")
    transported_by = models.CharField(max_length=64, blank=True)
    transportation_comments = models.TextField(blank=True)

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
    supervisor = models.ForeignKey(Approver, on_delete=models.CASCADE,
        verbose_name="Approving Supervisor")
    standards = models.TextField("Unit(s) of Study / Curriculum Standards Addressed During Trip",
        help_text="Please be specific.")
    anticipatory = models.TextField("Description of Anticipatory Activity",
        help_text="To be completed with students in advance of trip")
    purpose = models.TextField("Description of Educational Value of Trip",
        help_text="What will the students learn, and HOW?")

    # Nurse
    nurse_required = models.NullBooleanField()
    nurse_comments = models.TextField(blank=True)
    nurse_name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.destination

    def total(self):
        return self.chaperone_set.count() + self.pupils + self.teachers

    def clean_approvals(self):
        """
        If a role has multiple approvers, we only need 1 response from
        that group. This removes unneeded approvals after someone responds
        """
        print("Removing unneeded approvals")
        for role in Role.objects.all():
            queryset = self.approval_set.filter(role=role)
            if queryset.filter(Q(approved=True) | Q(approved=False)).exists():
                for approval in queryset.filter(approved=None):
                    print("Removing unneeded approval {}".format(approval))
                    approval.delete()
                    
    def create_approvals(self, role):
        """
        Creates and saves approvals for a particular role
        """
        print("Creating approvals for {} {}".format(role, self.building))

        for approver in Approver.objects.filter(roles=role,
        building=field_trip.building):
            print("Creating approval for {}".format(approver))
            approval = Approval(approver=approver, field_trip=self, role=role,
                building=self.building)
            approval.save()
            print("Send email here")

    def process_approvals(self):
        """
        Creates and checks approvals as needed to see what the status of the
        form is. Should be run after every form change
        """

        # remove any unneeded approvals
        self.clean_approvals()

        # Nurses
        role = Role.objects.filter(code='NURSE')
        queryset = self.approval_set.filter(role=role)
        if not queryset.exists(): # no approvals, create them
            self.create_approvals(role)
            return "In Progress"
        elif queryset.filter(approved=None).exists(): # not completed yet
            return "In Progress"
        elif queryset.filter(approved=False).exists(): # denied
            return "Denied"

        # otherwise it has been approved
        return "Approved"

class Chaperone(models.Model):
    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# NOTE: Approvers can have multiple buildings and roles but an Approval can only
# be for ONE role and ONE building
class Approval(models.Model):

    approver = models.ForeignKey(Approver, on_delete=models.CASCADE)
    approved = models.NullBooleanField()
    comments = models.TextField(blank=True)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True, null=True)
