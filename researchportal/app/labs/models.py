from django.db import models

# Create your models here.


class Labs(models.Model):
    """Lab Model"""

    name = models.CharField(max_length=255)

    # Once a department is created, it cannot be deleted
    # To delete a department, you need to delete all the labs,
    # Under the department, and then delete the department
    department = models.ForeignKey("Department", on_delete=models.PROTECT)

    # A brief description of the lab
    description = models.TextField(max_length=1e4)
