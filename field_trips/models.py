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
    status = models.CharField(max_length=64, default="In Progress")
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

    def add_approval(self, role, building=None):
        print("Creating new approval for {} {}".format(role, building))
        Approval(field_trip=self, role=role, building=building).save()
        approvers = Approver.objects.filter(roles=role)
        if building:
            approvers = approvers.filter(building=building)
        for approver in approvers:
            print("Emailing notification to {}".format(approver))

    def check_or_add_approval(self, code, building=None):
        role = Role.objects.filter(code=code)[0]
        print("Checking approval for {} {}".format(role, building))
        if not self.approval_set.filter(role=role).exists():
            self.add_approval(role, self.building)
            return "In Progress"
        elif self.approval_set.filter(role=role, approved=None).exists():
            return "In Progress"
        elif self.approval_set.filter(role=role, approved=False).exists():
            return "Denied"
        elif self.approval_set.filter(role=role, approved=True).exists():
            return "Approved"

    def process_approvals(self):
        """
        This should be called every time the form is changed. It sets up
        approvals, notifies approvers, and contains the primary logic for how
        a form is processed
        """
        # Only check approvals for forms that haven't yet been approved or
        # denied
        if self.status != "In Progress":
            return

        # The first four approvals have no conditions
        approvals = (
            ("NURSE", self.building),
            ("PRINCIPAL", self.building),
            ("SUPERVISOR", None),
            ("ASSISTANT SUPERINTENDENT", None)
        )

        for approval in approvals:
            result = self.check_or_add_approval(*approval)
            if result != "Approved":
                self.status = result
                return

        # if we need extra vehicles add an approval for facilities
        if len(self.vehicle_set) > 0:
            result = self.check_or_add_approval("FACILITES", None)
            if result != "Approved":
                self.status = result
                return

        # always add transportation
        result = self.check_or_add_approval("TRANSPORTATION", None)
        if result != "Approved":
            self.status = result
            return

        # if a nurse is requred add an approval for PPS
        if self.nurse_required:
            result = self.check_or_add_approval("PPS", None)
            if result != "Approved":
                self.status = result
                return

        # the field trip secretary will approve it once it is approved by the
        # board
        result = self.check_or_add_approval("FIELDTRIP SECRETARY", None)
        if result != "Approved":
            self.status = result
            return

        self.status = "Approved"
        return

    def first_needed_approval_for_approver(self, approver):
        """
        Returns the first approval needed for a particular approver. If there
        is no approval needed for that approver it returns None.
        """
        if not self.status == "In Progress":
            return None

        for approval in self.approval_set.filter(approved=None):
            if approval.role in approver.roles.all():
                if approval.building:
                    if approval.building in approver.building_set.all():
                        return approval
                else:
                    return approval
        return None

class Chaperone(models.Model):
    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# NOTE: Approvers can have multiple buildings and roles but an Approval can only
# be for ONE role and ONE building
class Approval(models.Model):

    class Meta:
        ordering = ['timestamp']

    approver = models.ForeignKey(Approver, on_delete=models.CASCADE,
        blank=True, null=True)
    approved = models.NullBooleanField()
    comments = models.TextField(blank=True)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE,
        blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Role: {}, Building: {}, Approver: {}, Approved: {}".format(
            self.role, self.building, self.approver, self.approved)
