from django.db import models
from django.db.models.enums import IntegerChoices
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # This model will not create a table, it will be used as base-class
        # for other tables
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ["-created_at", "-updated_at"]

class Labs(models.Model):
    """Lab Model"""

    name = models.CharField(max_length=255)

    # Once a department is created, it cannot be deleted
    # To delete a department, you need to delete all the labs,
    # Under the department, and then delete the department
    department = models.ForeignKey("Department", on_delete=models.PROTECT)

    # A brief description of the lab
    description = models.TextField(max_length=1e4)

class Project(TimestampedModel):
    """Project (aka Research Group) Model"""

    name = models.CharField(max_length=255)

    # creating a index for slug, to easy readable url generation and fast look up
    # we shd be able to look-up a project with both id and slug
    # even though slug is preferred
    slug = models.SlugField(db_index=True, max_length=255, unique=True)

    # A short abstract about the Project, size < 10,000 char
    abstract = models.TextField(max_length=1e4)

    # A link to google scholar paper
    # TODO: add validators to make sure link added is valid
    paper_link = models.URLField()

    # Department which the project belongs to,
    # Generally the Department the Head Prof is from
    #
    # A project can have multiple "Areas of Research" from different departments.
    # But it can only belong to one department.
    department = models.ForeignKey("Department", on_delete=models.PROTECT)

    # Owner of the project, aka person with admin rights.
    head = models.ForeignKey("User", on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        # When creating a new project,
        # add a project creator, with admin privilege
        pass

    def __str__(self):
        """Returns name of project - author"""
        # TODO
        pass


class ProjectMemberRelationship(models.Model):
    """Project Member Relation Model
    Contains the project and member relationship, along with that user's privilege.
    Prof who creates the Project will automatically be given the admin role.
    And No-one else can have that role."""

    project_id = models.ForeignKey("Project", on_delete=models.CASCADE)
    user_id = models.ForeignKey("User", on_delete=models.CASCADE)

    # One cannot delete a Privilege after it has been created
    privilege = models.ForeignKey("ProjectMemberPrivilege", on_delete=models.PROTECT)


class ProjectMemberPrivilege(models.Model):
    """Different permission levels for the members
    of a project.
    1. View (Default): No Write or edit access, can only
    view the contents of the page.
    2. Write : Can edit the details (Abstract and Google Scholar link for now)
    3. Edit : Can edit the Area of research of the project + WRITE Privilege
    This is the highest privilege that can be assigned.
    4. Admin : Can add members to users and assign privilege to the users.
    Prof who creates the Project will automatically be given the admin role.
    And No one else can have that role."""

    class AvailablePrivileges(models.IntegerChoices):
        """Text Choice for allowed privileges."""

        VIEW = 1, _("View")
        WRITE = 2, _("Write")
        EDIT = 3, _("Edit")
        ADMIN = 4, _("Admin")

    code = models.IntegerField(choices=AvailablePrivileges.choices)

    # human readable privilege name
    name = models.CharField(max_length=25)

    def __init__(self, *args, **kwargs):
        # TODO
        pass


class AreaOfResearch(models.Model):
    """Area of Research Model"""

    name = models.CharField(max_length=255, unique=True)

    slug = models.SlugField(max_length=255, db_index=True)

    # Every Area Of Reseach must belong to a department,
    # A project from any department, can belong
    # to a research group of any department
    #
    # The only reason Area of Research has a department,
    # is to display them in department page
    department = models.ForeignKey("Department", on_delete=models.PROTECT)


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
    role = models.CharField(max_length=2, choices=UserRoles.choices, default=UserRoles.STUDENT)
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

    full_name = models.CharField(unique=True, max_length=50)
    short_name = models.CharField(max_length=3)


