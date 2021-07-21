from django.db import models
from django.db.models.enums import IntegerChoices
from django.utils.translation import gettext_lazy as _
from app.core.models import TimestampedModel

# Create your models here.

# TODO: Slugify this
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


class ProjectMemberRelationship(models.Model):
    """Project Member Relation Model
    Contains the project and member relationship, along with that user's privilege.
    Prof who creates the Project will automatically be given the admin role.
    And No-one else can have that role."""

    project_id = models.ForeignKey("Project", on_delete=models.CASCADE)
    user_id = models.ForeignKey("Member", on_delete=models.CASCADE)

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

    code = models.IntegerField(choices=IntegerChoices)

    # human readable privilege name
    name = models.CharField()

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
