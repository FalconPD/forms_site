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

class Building(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Approver(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    roles = models.ManyToManyField(Role)
    buildings = models.ManyToManyField(Building)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{} {}'.format(self.name, self.title)

class FieldTrip(models.Model):
    # Status
    ARCHIVED = 0
    IN_PROGRESS = 1
    APPROVED = 2
    DENIED = 3
    DROPPED = 4
    DRAFT = 5
    STATUS_CHOICES = (
        (ARCHIVED, "Archived"),
        (IN_PROGRESS, "In Progress"),
        (APPROVED, "Approved"),
        (DENIED, "Denied"),
        (DROPPED, "Dropped"),
        (DRAFT, "Draft"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=IN_PROGRESS)

    # update() creates approvals, but can't save them until AFTER this field
    # trip is saved. This keeps track of the approvals we need to save.
    new_approvals = []

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

    def save(self, *args, **kwargs):
        """
        Runs the update command every time this model is saved. It also saves
        all the related approvers as update may add them
        """
        self.update()
        super().save(*args, **kwargs)
        import pdb; pdb.set_trace()
        for approval in self.new_approvals:
            approval.field_trip = self # why can't I set this in add_approval()?
            approval.save()

    def __str__(self):
        return self.destination

    def total(self):
        return self.chaperone_set.count() + self.pupils + self.teachers

    def add_approval(self, role, building=None):
        """
        Creates a new, unsigned approval for a role, building and notifies
        possible approvers.
        """
        print("Creating new approval for {} {}".format(role, building))
        self.new_approvals.append(
            Approval(role=role, building=building)
        )
        approvers = Approver.objects.filter(roles=role)
        if building:
            approvers = approvers.filter(buildings=building)
        for approver in approvers:
            print("Emailing notification to {}".format(approver))

    def check_approval(self, code, building):
        """
        Checks to see if there is an approval for a given role, building. Adds
        the approval if needed. Returns True if the update function should
        continue.
        """
        role = Role.objects.filter(code=code)[0]
        print("Checking approval for {} {}".format(role, building))
        if not self.approval_set.filter(role=role).exists():
            self.add_approval(role, building)
            return False
        elif self.approval_set.filter(role=role, approved=None).exists():
            return False
        elif self.approval_set.filter(role=role, approved=False).exists():
            self.status = self.DENIED
            return False
        elif self.approval_set.filter(role=role, approved=True).exists():
            return True

    def check_approval_if_extra_vehciles(self, code, building):
        if len(self.vehicle_set) > 0:
            print("Extra vehicles are needed on this trip")
            return self.check_approval(code, building)
        else:
            return True

    def check_approval_if_nurse_needed(self, code, building):
        if self.nurse_required:
            print("A nurse is needed on this trip")
            return self.check_approval(code, building)
        else:
            return True

    def update(self):
        """
        This is called every time the form is saved BEFORE it is commited to
        the database. It sets up approvals, notifies approvers, and contains
        the primary logic for how a form is processed
        """
        # Only check approvals for forms that are active
        if self.status != self.IN_PROGRESS:
            return

        steps = [
            (self.check_approval, ("NURSE", self.building)),
            (self.check_approval, ("PRINCIPAL", self.building)),
            (self.check_approval, ("SUPERVISOR", None)),
            (self.check_approval, ("ASSISTANT SUPERINTENDENT", None)),
            (self.check_approval_if_extra_vehicles, ("FACILITIES", None)),
            (self.check_approval, ("TRANSPORTATION", None)),
            (self.check_approval_if_nurse_needed, ("PPS", None)),
            (self.check_approval, ("FIELDTRIP SECRETARY", None)),
        ]

        for step, args in steps:
            if not step(*args):
                return

        # if we've made it this far, we are approved by everyone and the board
        self.status = self.APPROVED
        return

    def first_needed_approval_for_approver(self, approver):
        """
        Returns the first approval needed for a particular approver. If there
        is no approval needed for that approver it returns None.
        """
        if not self.status != self.IN_PROGRESS:
            return None

        for approval in self.approval_set:
            if approval.can_sign(approver):
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
    approved = models.NullBooleanField("Do you approve this field trip?")
    comments = models.TextField(blank=True)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE,
        blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Role: {}, Building: {}, Approver: {}, Approved: {}".format(
            self.role, self.building, self.approver, self.approved)

    def can_sign(self, approver):
        """
        Checks to see if this approval can be signed by an approver. Prevents
        signing something multiple times.
        """
        if self.approved != None or self.approver != None:
            return False
        if not self.role in approver.roles.all():
            return False
        if self.building:
            if not self.building in approver.buildings.all():
                return False
        return True
