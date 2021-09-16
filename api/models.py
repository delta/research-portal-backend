from django.db import models
from django.db.models.enums import IntegerChoices
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import os

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
    image_url = models.URLField(max_length=255, blank=True, null=True)

class COE(models.Model):
    """Lab Model"""

    name = models.CharField(max_length=255)
    # A brief description of the COE
    description = models.TextField(max_length=1e4)
    image_url = models.URLField(max_length=255, blank=True, null=True)


class AreaOfResearch(models.Model):
    """Area of Research Model"""

    name = models.CharField(max_length=255, unique=True)

    description = models.TextField(max_length=1e4)

    # Every Area Of Reseach must belong to a department,
    # A project from any department, can belong
    # to a research group of any department
    #
    # The only reason Area of Research has a department,
    # is to display them in department page
    department = models.ForeignKey("Department", on_delete=models.PROTECT)

class Project(TimestampedModel):
    """Project (aka Research Group) Model"""

    name = models.CharField(max_length=255)

    # AOR
    # aor = models.ForeignKey("AreaOfResearch", on_delete=models.PROTECT)
    aor_tags = models.ManyToManyField(AreaOfResearch)
    tags = ArrayField(
        models.CharField(max_length=25), 
        default=list, 
        blank=True,
    )
    labs_tags = models.ManyToManyField(Labs)
    coe_tags = models.ManyToManyField(COE)
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


class ProjectMemberRelationship(models.Model):
    """Project Member Relation Model
    Contains the project and member relationship, along with that user's privilege.
    Prof who creates the Project will automatically be given the admin role.
    And No-one else can have that role."""

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

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


class UserManager(BaseUserManager):
    """Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.
    All we have to do is override the `create_user` function which we will use
    to create `User` objects."""

    def _create_user(self, email, name, password, **extra_details):
        """
        Creates and saves a User with the given email and password
        """

        if not email:
            raise ValueError('The given email must be set')

        if name is None:
            raise ValueError('Name cannot be empty')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_details)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_details):
        """
        Creates and saves a user with the given email, password
        """
        print(extra_details)
        extra_details.setdefault('is_superuser', False)
        return self._create_user(email, name, password, **extra_details)

    def create_superuser(self, email, name, password, **extra_details):
        """
        Creates and saves a user with the given email, password
        """

        extra_details.setdefault('is_superuser', True)

        if extra_details.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, name, password, **extra_details)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """User Model"""
    
    name = models.CharField(max_length=255, default=None, unique=False)
    email = models.EmailField(max_length=255, unique=True)
    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)
    class AvailableAdminLevels(models.TextChoices):
        """Text Choice for Available Admin Levels.
        1. Normal : Default value, no special privileges
        2. Department : Has Admin Privileges for all projects in that department
        3. Global : Has Admin Privileges for all projects in the system 
        """

        NORMAL = "Normal", _("Normal")
        DEPARTMENT = "Department", _("Department")
        GLOBAL = "Global", _("Global")

    admin_level = models.CharField(max_length=25, choices=AvailableAdminLevels.choices, default=AvailableAdminLevels.NORMAL)

    dept = models.ForeignKey("Department", on_delete=models.DO_NOTHING)
    image = models.FileField(null=True,blank=True,upload_to='media/documents/')
    
    @property
    def image_url(self):
        from django.contrib.sites.models import Site

        domain = Site.objects.get_current().domain
        url = os.environ.get('BACKEND_ROOT_APP_URL', 'http://localhost:8000')

        if self.image and hasattr(self.image, 'url'):
            return url + self.image.name

    is_verified = models.BooleanField(default=False)
    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

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
        ME = "MECH", _("Mechanical Engineering")
        ICE = "ICE", _("Instrumentation & Communication Engineering")
        CE = "CHEM", _("Chemical Engineering")
        CL = "CIVIL", _("Civil Engineering")
        PR = "PROD", _("Production Engineering")
        MME = "META", ("Metallurgical & Materials Engineering")
        DEE = "DEE", _("Energy and Environment (CEESAT)")
        MA = "MATHS", _("Mathematics")
        PH = "PHYSICS", _("Physics")
        HU = "HUMANITIES", _("Humanities")
        AR = "ARCHITECTURE", _("Architecture")
        MS = "MS", _("Management Studies")
        MAINTAINER = "XX", _("Maintainer")  # Special dept for all super-admins

    full_name = models.CharField(unique=True, max_length=50)
    short_name = models.CharField(max_length=15)
    image_url = models.URLField(max_length=255, blank=True, null=True)


