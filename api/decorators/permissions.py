import logging
from django.contrib.sessions.models import Session
from api.controllers.response_format import unauthorized_response, error_response
from api.models import User, Project, ProjectMemberRelationship, ProjectMemberPrivilege
from django.http import HttpRequest
logger = logging.getLogger('django')

def IsStaffDec(view):
    '''
    Checks if is_staff to create projects.
    '''

    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            assert isinstance(request, HttpRequest)
            user_id = request.session.get('user_id')
            session_key = request.session.session_key
            user_session = Session.objects.get(pk=session_key)
            assert user_session.get_decoded().get('user_id') == user_id
            user = request.user
            if user.is_staff:
                request.is_staff = True
            else:
                request.is_staff = False
        except Exception as e:
            logger.info('IsStaff Decorator: Unauthorized response')
            return unauthorized_response()
        return view(*args, **kwargs)
    return wrapper

def CheckAccessPrivilegeDec(view):
    '''
    Checks the Access Privilege and puts it in request.
    '''

    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            assert isinstance(request, HttpRequest)
            user_id = request.session.get('user_id')
            session_key = request.session.session_key
            user_session = Session.objects.get(pk=session_key)
            assert user_session.get_decoded().get('user_id') == user_id
            user = request.user
            project_id = request.GET.get("projectId")
            print(project_id)
            if not project_id:
                project_id = request.POST.get("projectId")
            print(project_id)
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return error_response("Project does not exist")
            
            if project.head == user:
                request.access_privilege = "admin"
            else:
                try:
                    project_member_relationship = ProjectMemberRelationship.objects.get(user=user,project=project)
                except ProjectMemberRelationship.DoesNotExist:
                    return error_response("User is not a member of the project")

                request.access_privilege = project_member_relationship.privilege.name

        except Exception as e:
            logger.info('CheckAccessPrivilege Decorator: Unauthorized response')
            return unauthorized_response()
        return view(*args, **kwargs)
    return wrapper
