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
            if 'user_id' in request.session:
                user_id = request.session.get('user_id')
                session_key = request.session.session_key
                user_session = Session.objects.get(pk=session_key)
                assert user_session.get_decoded().get('user_id') == user_id
                user = request.user 
                project_id = request.GET.get("projectId")
                if not project_id:
                    project_id = request.POST.get("projectId")
                try:
                    project = Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    return error_response("Project does not exist")
                
                if project.head == user:
                    request.access_privilege = "admin"
                else:
                    try:
                        project_member_relationship = ProjectMemberRelationship.objects.get(user=user,project=project)
                        request.access_privilege = project_member_relationship.privilege.name
                    except ProjectMemberRelationship.DoesNotExist:
                        request.access_privilege = "view"
            else:
                request.access_privilege = "view"
        except Exception as e:
            logger.info(e)
            logger.info('CheckAccessPrivilege Decorator: Unauthorized response')
            return unauthorized_response()
        return view(*args, **kwargs)
    return wrapper

def IsAdmin(view):
    '''
    Checks if current user is admin to the particular project.
    '''

    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            assert isinstance(request, HttpRequest)
            user_id = request.session.get('user_id')
            session_key = request.session.session_key
            user_session = Session.objects.get(pk=session_key)
            assert user_session.get_decoded().get('user_id') == user_id
            user = User.objects.get(id=user_id)
            project_id = request.POST.get('project_id')
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return error_response('Project does not exist')
            if project.head == user:
                request.is_admin = True
            else:
                request.is_admin = False
                return error_response('User is not an admin to the requested project')
        except Exception as e:
            logger.error(e)
            logger.info('IsAdmin Decorator: Unauthorized response')
            return unauthorized_response()
        return view(*args, **kwargs)
    return wrapper
