from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from app.core.models import TimestampedModel


class UserManager(BaseUserManager):
    """Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects."""

    def create_user(self, roll_no):
        # hit ldap and create a new user

        # need to figure out how to create a profile
        # for the newly created user

        pass

    def create_superuser(self, roll_number, password):
        """Create and return a `User` with superuser powers.

        Superuser powers means that this use is an admin that can do anything
        they want."""
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(roll_number, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """User Model"""

    roll_number = models.IntegerField(unique=True, db_index=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the roll number
    USERNAME_FIELD = "roll_number"
    REQUIRED_FIELDS = ["roll_number"]

    objects = UserManager()


class Profile(TimestampedModel):
    """Profile Model"""

    class UserRoles(models.TextChoices):
        """Different roles a user can have. Site maintainers will have Admin role"""

        STUDENT = "ST", _("Student")
        PROFESSOR = "PR", _("Professor")
        ASSISTANT_PROFESSOR = "AP", _("Assistant Professor")
        ADMIN = "AD", _("Admin")

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=2, choices=UserRoles, default=UserRoles.STUDENT)
    dept = models.ForeignKey("Department", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

    @property
    def getRole(self):
        """Returns the role of the user"""
        return self.role.label


class Department(models.Model):
    """Department Model

    Be careful before adding a new department, Once a department is created
    you have to delete all the "Areas of Research", "Labs" and "Projects" before
    you can delete the department. It is better to seed all the Departments
    instead of adding them manually."""

    class DepartmentChoices(models.TextChoices):
        """All possible departments. There cannot be anyother departments."""

        CS = "CSE", _("Computer Science & Engineering")
        CA = "CA", _("Computer Applications")
        EC = "ECE", _("Electrical & Communication Engineering")
        EE = "EEE", _("Electrical & Electronics Engineering")
        ME = "ME", _("Mechanical Engineering")
        ICE = "ICE", _("Instrumentation & Communication Engineering")
        CE = "CE", _("Chemical Engineering")
        CL = "CL", _("Civil Engineering")
        PR = "PR", _("Production Engineering")
        MME = "MME", ("Metallurgical & Materials Engineering")
        DEE = "DEE", _("Energy and Environment (CEESAT)")
        MA = "MA", _("Mathematics")
        PH = "PH", _("Physics")
        HU = "HU", _("Humanities")
        AR = "AR", _("Architecture")
        MS = "MS", _("Management Studies")
        MAINTAINER = "XX", _("Maintainer")  # Special dept for all super-admins

    full_name = models.CharField(unique=True)
    short_name = models.CharField(max_length=3)

    # TODO add init func to add a full_name
