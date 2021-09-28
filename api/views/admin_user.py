from api.controllers.project_utilities import get_project_with_id
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
from api.models import  User, Department, ProjectMemberPrivilege, ProjectMemberRelationship, Project
from api.controllers.response_format import error_response
from api.decorators.permissions import IsAdmin
from api.decorators.response import JsonResponseDec
import logging
import json

logger = logging.getLogger(__name__)

class AllUsers(View):
    """
    return list of all professors' details
    """
    def get(self, req):
        try:
            users = User.objects.filter(is_staff=True, is_verified=True)
        except User.DoesNotExist:
            return error_response('Professors of given description not found')
        data = []
        for user in users:
            image_url = user.image_url
            user = model_to_dict(user)
            data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'is_verified': user['is_verified'],
                'is_staff': user['is_staff'],
                'image_url': image_url
            })
        return JsonResponse({
            'data': data
        })

@method_decorator(JsonResponseDec, name='dispatch')
class ProfileView(View):
    """
    return details of particular professor(project head)
    """
    def get(self, req):
        email = req.GET.get('email')
        projects = []
        projects_non_admin = []
        aors = []
        labs = []
        coes = []
        scholars = []
        try:
            profile = User.objects.get(email = email)
        except User.DoesNotExist:
            return error_response('profile does not exist')
        
        pmrs = ProjectMemberRelationship.objects.filter(user = profile) 
        
        profile_data = {
            **model_to_dict(profile, exclude=['image', 'department']),
            **{'image_url': profile.image_url },
            'department': model_to_dict(profile.dept)
        }
        
        for pmr in pmrs:
            cur_project = pmr.project.id
            
            project_data = get_project_with_id(cur_project)
            if project_data['success'] == False:
                continue
            
            if pmr.privilege.code == 4:
                projects.append(project_data)
                scholars += [member for member in project_data['members'] if (not member['is_staff']) and (member['email'] != profile.email)]
            else:
                projects_non_admin.append({'data': project_data, 'access': pmr.privilege.name})
            
            aors += project_data['aor_tags']
            aors = [dict(t) for t in {tuple(d.items()) for d in aors}]
            labs += project_data['labs_tags']
            labs = [dict(t) for t in {tuple(d.items()) for d in labs}]
            coes += project_data['coe_tags']
            coes = [dict(t) for t in {tuple(d.items()) for d in coes}]
        
        return {
            'data': profile_data,
            'scholars': scholars,
            'aors': aors,
            'coes': coes,
            'labs': labs,
            'projects': projects,
            'non_admin_projects': projects_non_admin
        }

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdmin, name='dispatch')
class AssignRoles(View):
    """
    pass an user, project and respective role to be updated
    1-View, 2-Write, 3-Edit, 4-Admin
    """
    def post(self, req):
        bodyData = json.loads(req.body)
        user_id = bodyData['user_id']
        project_id = bodyData['project_id']
        role = bodyData['role']
        try:
            user = User.objects.get(email=user_id)
        except User.DoesNotExist:
            return error_response('user does not exist')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return error_response('project does not exist')
        try:
            pmp = ProjectMemberPrivilege.objects.get(code=role)
        except ProjectMemberPrivilege.DoesNotExist:
            return error_response('projectmemberprivilege does not exist')
        try:
            pmr = ProjectMemberRelationship.objects.get(project=project,user=user)
        except ProjectMemberRelationship.DoesNotExist:
            return error_response('projectmemberrelationship does not exist')
        
        pmr.privilege = pmp
        pmr.save()

        return ({
            'data': 'updated successfully !'
        })

class CreateTags(View):
    def post(self, req):
        pass

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdmin, name='dispatch')
class AddMembers(View):
    """
    add members of specified role to a project if not already present
    """
    def post(self, req):
        userData = json.loads(req.body)
        user_id = userData['user_id']
        project_id = userData['project_id']
        role = userData['role']
        try:
            user = User.objects.get(email=user_id)
        except User.DoesNotExist:
            return error_response('user does not exist !')
        # print(user[0])
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return error_response('project does not exist !')
        try:
            pmp = ProjectMemberPrivilege.objects.get(code=role)
        except ProjectMemberPrivilege.DoesNotExist:
            return error_response('projectmemberprivilege does not exist !')
        if not ProjectMemberRelationship.objects.filter(user=user,project=project).exists():
            pmr = ProjectMemberRelationship.objects.create(project=project,user=user,privilege=pmp)
        else:
            return error_response('The project-member relationship already exists')
        return ({
            'data': 'Added Successfully !'
        })

@method_decorator(JsonResponseDec, name='dispatch')
class Search(View):
    def get(self, req):
        professorName = req.GET.get("professor")
        professors = User.objects.filter(Q(name__unaccent__icontains=professorName) & Q(
            is_staff=True))
        data = []
        for user in professors:
            image_url = user.image_url
            user = model_to_dict(user)
            data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'is_verified': user['is_verified'],
                'is_staff': user['is_staff'],
                'image_url': image_url
            })
        return {
            'data': data
        }

class RenderImage(View):
    """
    return the image of provided url
    """
    def get(self, req):
        try:
            image_url = req.GET.get('image_url')
            image_url = image_url[1:]
            img = open(image_url, 'rb')
            response = FileResponse(img)
            return response
        except Exception as e:
            logger.error(e)
            return error_response('Failed to fetch image file')
