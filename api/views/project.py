from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.views.generic import View
from api.decorators.response import JsonResponseDec
from api.decorators.permissions import IsStaffDec, CheckAccessPrivilegeDec
from api.models import AreaOfResearch, Department, Project, ProjectMemberRelationship, User, Labs, COE
from api.controllers.response_format import error_response
from api.controllers.project_utilities import create_project, get_project_with_id
from django.db.models import Q
import logging
import json

logger = logging.getLogger(__name__)


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
        data = []
        projects = Project.objects.all()
        
        for proj in projects:
            rel_obj = {
            **model_to_dict(proj, exclude=['aor_tags', 'labs_tags', 'coe_tags']),
            **{'image_url': proj.head.image_url},
            'aor_tags': [model_to_dict(tag) for tag in proj.aor_tags.all()],
            'labs_tags': [model_to_dict(tag) for tag in proj.labs_tags.all()],
            'coe_tags': [model_to_dict(tag) for tag in proj.coe_tags.all()]
            }
            data.append(rel_obj)
            
        return {
            'data': data
        }


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class ProjectWithId(View):
    """
    Return a Projects with id
    """

    def get(self, req):
        id = req.GET.get("projectId")
        project_response = get_project_with_id(id)
        if project_response['success'] == False:
            return error_response("Project doesn't exist")
        return {
            'data': project_response,
            'privilege': req.access_privilege
        }


@method_decorator(JsonResponseDec, name='dispatch')
class Search(View):
    def get(self, req):
        projectName = req.GET.get("projectName")
        department = req.GET.get("department")
        areaOfResearch = req.GET.get("aor")
        coe = req.GET.get("coe")
        lab = req.GET.get("lab")
        tag = req.GET.get("tag")
        headName = req.GET.get("headName")
        allProjs = Project.objects.all()

        projects = Project.objects.filter(
            Q(head__name__unaccent__icontains = headName)
            & Q(name__unaccent__icontains = projectName)
            & Q(department__short_name__unaccent__icontains=department)
            & Q(tags__icontains = tag)
        ).distinct()

        if areaOfResearch != "":
            projects = projects.filter(aor_tags__name__unaccent__icontains=areaOfResearch)
        if coe != "":
            projects = projects.filter(coe_tags__name__unaccent__icontains = coe).distinct()
        if lab != "":
            projects = projects.filter(labs_tags__name__unaccent__icontains = lab).distinct()

        data = []
        for proj in projects:
            rel_obj = {
            **model_to_dict(proj, exclude=['aor_tags', 'labs_tags', 'coe_tags']),
            **{'image_url': proj.head.image_url},
            'aor_tags': [model_to_dict(tag) for tag in proj.aor_tags.all()],
            'labs_tags': [model_to_dict(tag) for tag in proj.labs_tags.all()],
            'coe_tags': [model_to_dict(tag) for tag in proj.coe_tags.all()]
            }
            data.append(rel_obj)
        return {
            'data': data
        }

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class GetPrivilege(View):
    """
        Returns the privilege of a user
    """
    def get(self, req):
        return {
            'data': req.access_privilege
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
        projectData = json.loads(req.body)
        name = projectData["name"]
        paper_link = projectData["paperLink"]
        head = projectData["head"]
        department = projectData["department"]
        abstract = projectData["abstract"]
        aor = projectData["aor"]
        labs = projectData["labs"]
        tags = projectData["tags"]
        coes = projectData["coes"]

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
            if create_project(name, abstract, paper_link, user, department_obj, tags, aor, labs, coes):
                logger.info(
                    'Project(name={}) creation successful'.format(name))
                return "Project created successfully!"
            else:
                return error_response("Invalid details")
        except Exception as e:
            logger.error(e)
            return error_response("Project creation failed")


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class Write(View):
    """
        Updates following details in a project if user has "Write" access
        1. Abstract
        2. google Scholar's link
    """

    def post(self, req):
        projectData = json.loads(req.body)
        abstract = projectData["abstract"]
        paper_link = projectData["paperLink"]
        project_id = req.GET.get("projectId")

        if not (req.access_privilege == "Write" or req.access_privilege == "Admin"):
            return error_response("USER DOESN'T HAVE WRITE ACCESS")
        try:
            project = Project.objects.get(id=project_id)
            project.paper_link = paper_link
            project.abstract = abstract
            project.save()
            logger.info(
                'Project(name={}) update successful'.format(project.name))
            return "Project updated successfully!"
        except Project.DoesNotExist:
            return error_response("Project doesn't exist")


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class Edit(View):
    """
        Updates following details in a project if user has "Edit" access
        1. Abstract
        2. google Scholar's link
        3. Area of research
        4. Labs
        5. Coes
        6. Tags
        Updates following details also in a project if user has "Admin" access
        1. Project Name
    """

    def post(self, req):
        projectData = json.loads(req.body)
        abstract = projectData["abstract"]
        paper_link = projectData["paperLink"]
        name = projectData["name"]
        aor = projectData["aor"]
        labs = projectData["labs"]
        coes = projectData["coes"]
        tags = projectData["tags"]
        project_id = req.GET.get("projectId")

        if not (req.access_privilege == "Edit" or req.access_privilege == "Admin"):
            return error_response("USER DOESN'T HAVE EDIT ACCESS")
        try:
            project = Project.objects.get(id=project_id)
            if Project.objects.filter(paper_link=paper_link).exists() and paper_link != project.paper_link:
                return error_response("Google scholar's link already exists")
            project.paper_link = paper_link
            project.abstract = abstract
            aor_set = AreaOfResearch.objects.filter(name__in=aor)
            labs_set = Labs.objects.filter(name__in=labs)
            coes_set = COE.objects.filter(name__in=coes)
            project.aor_tags.clear()
            project.labs_tags.clear()
            project.coe_tags.clear()
            project.aor_tags.add(*aor_set)
            project.labs_tags.add(*labs_set)
            project.coe_tags.add(*coes_set)
            project.tags = tags
            if name != project.name and Project.objects.filter(name=name).exists():
                return error_response("A project with the same name exists! Please switch to a new project name")
            if req.access_privilege == "Admin":
                project.name = name
            project.save()
            logger.info(
                'Project(name={}) edit successful'.format(project.name))
            return "Project edited successfully!"
        except Exception as e:
            logger.error(e)
            return error_response("Project edit failed")
