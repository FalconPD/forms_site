import inspect

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Discipline(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title

class Role(models.Model):
    PRINCIPAL = 0
    NURSE = 1
    SUPERVISOR = 2
    ASSISTANT_SUPERINTENDENT = 3
    FIELD_TRIP_SECRETARY = 4
    PPS = 5
    FACILITIES = 6
    TRANSPORTATION = 7
    ROLE_CHOICES = (
        (PRINCIPAL, "Principal"),
        (NURSE, "Nurse"),
        (SUPERVISOR, "Supervisor"),
        (ASSISTANT_SUPERINTENDENT, "Assistant Superintendent"),
        (FIELD_TRIP_SECRETARY, "Field Trip Secretary"),
        (PPS, "Secretary of Pupil Personnel Services"),
        (FACILITIES, "Head of Facilites"),
        (TRANSPORTATION, "Secretary of Transportation"),
    )
    code = models.IntegerField(choices=ROLE_CHOICES)
    building = models.ForeignKey(Building, on_delete=models.CASCADE,
        null=True, blank=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE,
        null=True, blank=True)

    def __str__(self):
        text = "{}".format(self.ROLE_CHOICES[self.code][1])
        if self.building:
            text += ", {}".format(self.building)
        if self.discipline:
            text += ", {}".format(self.discipline)
        return text

class Approver(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=64)
    roles = models.ManyToManyField(Role)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class FieldTrip(models.Model):
    # Status
    ARCHIVED = 0
    IN_PROGRESS = 1
    APPROVED = 2
    DENIED = 3
    DROPPED = 4
    DRAFT = 5
    PENDING = 6
    STATUS_CHOICES = (
        (ARCHIVED, "Archived"),
        (IN_PROGRESS, "In Progress"),
        (APPROVED, "Approved"),
        (DENIED, "Denied"),
        (DROPPED, "Dropped"),
        (DRAFT, "Draft"),
        (PENDING, "Pending Board Approval"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=IN_PROGRESS)
    log_text = models.TextField(default="")

    # General Info
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted = models.DateTimeField("Submitted", auto_now_add=True)
    destination = models.CharField(max_length=64, blank=True)
    group = models.CharField("Class / Group / Club", max_length=64, blank=True)
    grades = models.ManyToManyField(Grade, blank=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, blank=True)
    roster = models.FileField(upload_to="field_trips/", blank=True)
    itinerary = models.TextField(help_text=
        ("Please include time at destination, lunch arrangements, and "
         "additional stops."), blank=True)
    pupils = models.IntegerField("Number of Pupils", blank=True, null=True)
    teachers = models.IntegerField("Number of Teachers", blank=True, null=True)
    departing = models.DateTimeField("Date and Time of Departure", blank=True,
        null=True)
    returning = models.DateTimeField("Date and Time Returning to School",
        blank=True, null=True)

    # Transportation
    directions = models.FileField(upload_to="field_trips/", blank=True)
    buses = models.IntegerField("Number of Buses Required", help_text="Each bus seats 52 people.", blank=True)
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
        "Please describe all costs in detail. Buses are $75 per hour.",
        blank=True)
    funds = models.CharField("Source of Funds", max_length=8,
        choices=SOURCE_OF_FUNDS_CHOICES, blank=True)

    # Curricular Tie Ins
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE,
        help_text="Used to select supervisor for approval", blank=True,
        verbose_name="Discipline")
    standards = models.TextField(
        "Unit(s) of Study / Curriculum Standards Addressed During Trip",
        help_text="Please be specific.", blank=True)
    anticipatory = models.TextField("Description of Anticipatory Activity",
        help_text="To be completed with students in advance of trip",
        blank=True)
    purpose = models.TextField("Description of Educational Value of Trip",
        help_text="What will the students learn, and HOW?",
        blank=True)

    # Nurse
    nurse_required = models.NullBooleanField()
    nurse_comments = models.TextField(blank=True)
    nurse_name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return "{} to {} on {}".format(self.group, self.destination,
            self.departing)

    def log(self, text):
        self.log_text += "{}: {}\n".format(timezone.now(), text)

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

    def total(self):
        return self.chaperone_set.count() + self.pupils + self.teachers

    @classmethod
    def lookup_status(cls, status):
        for choice, text in cls.STATUS_CHOICES:
            if choice == status:
                return text
        return None

    def print_status(self):
        return self.lookup_status(self.status)

    def print_update_source(self):
        return inspect.getsource(self.update)

    def send_approval_request(self, approver):
        self.log("Sending approval request to {}".format(approver))
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

    def add_approval(self, role):
        """
        Creates a new, unsigned approval for a role. Also notifies possible
        approvers via email.
        """
        self.log("Creating new approval for {}".format(role))
        Approval(field_trip=self, role=role).save()

        for possible_approver in Approver.objects.filter(roles=role).all():
            self.send_approval_request(possible_approver)

    class InProgress(Exception):
        pass

    class Denied(Exception):
        pass

    def lookup_role(self, role_code, building=None, discipline=None):
        """
        Find a role based on it's code and optionally a building and
        discipline
        """
        query = Role.objects.filter(code=role_code)
        if building:
            query = query.filter(building=building)
        if discipline:
            query = query.filter(discipline=discipline)
        return query.get()

    def check_approval(self, role_code, building=None, discipline=None):
        """
        Checks to see if there is an approval for a given role_code and
        building. Adds the approval if needed. Raises a Denied or InProgress
        exception accordingly.
        """
        role = self.lookup_role(role_code, building, discipline)
        self.log("Checking approval for {}".format(role))

        # Find the approvals that meet our criterea
        approvals = self.approval_set.filter(role=role)

        # If we can't find any, add one
        if not approvals.exists():
            self.add_approval(role)
            raise self.InProgress

        # Just in case there are multiple, select the first
        approval = approvals.first()

        # If it is unsigned, raise InProgress
        if approval.approved == None:
            self.log("Still unsigned")
            raise self.InProgress

        # If it is denied, raise Denied
        if approval.approved == False:
            self.log("Denied by {}".format(approval.approver))
            raise self.Denied

        # otherwise it must be approved
        assert(approval.approved)
        self.log("Approved by {}".format(approval.approver))

    def update(self):
        """
        This is called every time the form is saved BEFORE it is commited to
        the database. It sets up approvals, notifies approvers, and contains
        the primary logic for how a form is processed
        """
        self.log("Running update")

        # Only check approvals for forms that are active
        if self.status != self.IN_PROGRESS:
            return

        try:
            self.check_approval(Role.NURSE, building=self.building)
            self.check_approval(Role.PRINCIPAL, building=self.building)
            self.check_approval(Role.SUPERVISOR, discipline=self.discipline)
            self.check_approval(Role.ASSISTANT_SUPERINTENDENT)
            if self.extra_vehicles.exists():
                self.check_approval(Role.FACILITIES)
            self.check_approval(Role.TRANSPORTATION)
            if self.nurse_required:
                self.check_approval(Role.PPS)
            self.check_approval(Role.FIELD_TRIP_SECRETARY)
        
            # if we've made it this far, we are just waiting on board approval
            self.log("Setting status to PENDING")
            self.status = self.PENDING
            return
        except self.InProgress:
            return
        except self.Denied:
            self.log("Setting status to DENIED")
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

class Approval(models.Model):

    class Meta:
        ordering = ['timestamp']

    approver = models.ForeignKey(Approver, on_delete=models.CASCADE,
        blank=True, null=True)
    approved = models.NullBooleanField("Do you approve this field trip?")
    comments = models.TextField(blank=True)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {} {}".format(self.role, self.approver, self.approved)

    def can_sign(self, approver):
        """
        Checks to see if this approval can be signed by an approver
        1. The approval has to be unsigned
        2. The approver has to have the required role
        """
        if self.approved != None:
            return False
        if not (self.role in approver.roles.all()):
            return False
        return True

class AdminOption(models.Model):
    window_open = models.BooleanField("Accepting requests", default=False)
    window_start = models.DateTimeField("Window Start")
    window_end = models.DateTimeField("Window End")
