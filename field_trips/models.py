from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

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
        Runs the update command every time this model is saved. When this
        object is first created, we may have to save() twice so that added
        approvals have an ID to reference us by
        """
        if not self.id:
            super().save(*args, **kwargs)
        self.update()
        super().save(args, kwargs)

    def __str__(self):
        return self.destination

    def total(self):
        return self.chaperone_set.count() + self.pupils + self.teachers

    def print_status(self):
        for choice, text in self.STATUS_CHOICES:
            if choice == self.status:
                return text
        return None

    def send_approval_request(self, approver):
        base = 'field_trips/email/approval_request'
        context = {
            'url': reverse('field_trips:approve_index'),
            'destination': self.destination,
            'first_name': self.submitter.first_name,
            'last_name': self.submitter.last_name,
            'email': self.submitter.email,
        }
        msg_plain = render_to_string(base + '.txt', context)
        send_mail(
            "Field Trip #{} Approval Requested".format(self.id),
            msg_plain,
            'forms@monroe.k12.nj.us',
            [approver.email],
        )

    class InProgress(Exception):
        pass

    class Denied(Exception):
        pass

    def add_approval(self, role, approver, building):
        """
        Creates a new, unsigned approval for a role and optional building,
        approver. Also notifies possible approvers via email.
        """
        print("Creating new approval for {} {} {}".format(role, approver,
            building))
        Approval(field_trip=self, role=role, building=building,
            approver=approver).save()

        if approver:
            self.send_approval_request(approver)
        else:
            possible_approvers = Approver.objects.filter(roles=role)
            if building:
                possible_approvers = possible_approvers.filter(
                    buildings=building)
            for possible_approver in possible_approvers.all():
                self.send_approval_request(possible_approver)

    def check_approval(self, code, building=None, approver=None):
        """
        Checks to see if there is an approval for a given role, approver,
        building. Adds the approval if needed. Raises a Denied or InProgress
        exception accordingly.
        """
        role = Role.objects.filter(code=code)[0]
        print("Checking approval for {} {} {}".format(role, approver, building))

        # Find the approvals that meet our criterea
        approvals = self.approval_set.filter(role=role)
        if approver:
            approvals = approvals.filter(approver=approver)
        if building:
            approvals = approvals.filter(building=building)

        # If we can't find any, add one
        if not approvals.exists():
            self.add_approval(role, approver, building)
            raise self.InProgress

        # Just in case there are multiple, select the first
        approval = approvals.all()[0]

        # If it is unsigned, raise InProgress
        if approval.approved == None:
            raise self.InProgress

        # If it is denied, raise Denied
        if approval.approved == False:
            raise self.Denied

        # otherwise it must be approved
        assert(approval.approved)

    def update(self):
        """
        This is called every time the form is saved BEFORE it is commited to
        the database. It sets up approvals, notifies approvers, and contains
        the primary logic for how a form is processed
        """
        # Only check approvals for forms that are active
        if self.status != self.IN_PROGRESS:
            return

        try:
            self.check_approval("NURSE", building=self.building)
            self.check_approval("PRINCIPAL", building=self.building)
            self.check_approval("SUPERVISOR", approver=self.supervisor)
            self.check_approval("ASSISTANT SUPERINTENDENT")
            if self.extra_vehicles.exists():
                self.check_approval("FACILITIES")
            self.check_approval, ("TRANSPORTATION")
            if self.nurse_required:
                self.check_approval("PPS")
            self.check_approval("FIELDTRIP SECRETARY")
        
            # if we've made it this far, we are approved by everyone
            self.status = self.APPROVED
            return
        except self.InProgress:
            return
        except self.Denied:
            self.status = self.DENIED
            return

    def first_needed_approval_for_approver(self, approver):
        """
        Returns the first approval needed for a particular approver. If there
        is no approval needed for that approver it returns None.
        """
        if self.status != self.IN_PROGRESS:
            return None

        for approval in self.approval_set.all():
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
        Checks to see if this approval can be signed by an approver
        1. The approval has to be unsigned
        2. If an approver is specified they have to be that approver
        3. The approver has to have the required role
        4. If a building is specified, the approver needs it
        """
        if self.approved != None:
            return False
        if self.approver:
            if self.approver != approver:
                return False
        if not (self.role in approver.roles.all()):
            return False
        if self.building:
            if not (self.building in approver.buildings.all()):
                return False
        return True
