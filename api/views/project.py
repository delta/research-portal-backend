from django.utils.decorators import method_decorator
from django.views.generic import View
from api.decorators.response import JsonResponseDec
from api.decorators.permissions import IsStaffDec
from api.models import AreaOfResearch, Department, Project, User
from api.controllers.response_format import error_response
from api.controllers.project_utilities import create_project
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)
from django.forms.models import model_to_dict

def list_to_dict(items):
    '''
    Converts a given QuerySet into a list of dictionaries
    '''
    converted = []
    for item in items:
        converted.append(model_to_dict(item))
    return converted

@method_decorator(JsonResponseDec, name='dispatch')
class AllProjects(View):
    """
    Return all Projects
    """
    def get(self, req):
        projects = Project.objects.all()
        return {
            'data': list_to_dict(projects)
        }

@method_decorator(JsonResponseDec, name='dispatch')
class Search(View):
    def get(self, req):
        query = req.GET.get("query")
        projects = Project.objects.filter(Q(head__name__unaccent__icontains = query) | Q(name__unaccent__icontains=query)| Q(aor__name__unaccent__icontains=query))
        return {
            'data': list_to_dict(projects)
        }

class Tags(View):
    def get(self, req):
        pass

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsStaffDec, name='dispatch')
class Create(View):
    """
        Creates a project if user has admin access and project details (link and name) are unique
    """
    def post(self, req):
        name = req.POST.get("name")
        paper_link = req.POST.get("paperLink")
        head = req.POST.get("email")
        department = req.POST.get("department")
        abstract = req.POST.get("abstract")
        aor = req.POST.get("areaOfResearch")
        
        if not req.is_staff:
            return error_response("PERMISSION DENIED TO CREATE PROJECTS")
        try:
            user = User.objects.get(email=head)
        except User.DoesNotExist:
            return error_response("User does not exist")
        
        if Project.objects.filter(paper_link=paper_link).exists():
            return error_response("Google scholar's link already exists")
        
        if Project.objects.filter(name=name).exists():
            return error_response("A project with the same name exists! Please switch to a new project name")
        
        try:
            department_obj = Department.objects.get(short_name=department)
        except Department.DoesNotExist:
            return error_response("Department doesn't exist")
        
        try:
            aor_obj = AreaOfResearch.objects.get(name = aor)
        except AreaOfResearch.DoesNotExist:
            return error_response("Please select from the given areas of research")
        
        try:
            if create_project(name, abstract, paper_link, user, department_obj, aor_obj):
                logger.info('Project(name={}) creation successful'.format(name))
                return "Project created successfully!"
            else:
                return error_response("Invalid details")
        except Exception as e:
            logger.error(e)
            return error_response("Project creation failed")

class Write(View):
    def post(self, req):
        pass

class Edit(View):
    def post(self, req):
        pass
