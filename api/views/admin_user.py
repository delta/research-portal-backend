from django.views.generic import View
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
from api.models import  User, Department, Profile, ProjectMemberPrivilege, ProjectMemberRelationship, Project
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
            users = User.objects.filter(is_staff=True)
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

class ProfileView(View):
    """
    return details of particular professor(project head)
    """
    def get(self, req):
        id = req.GET.get('profileId')
        data = []
        no_project = False
        no_scholars = False
        projects = []
        try:
            profile = Profile.objects.filter(user__id=id)
        except Profile.DoesNotExist:
            return error_response('profile does not exist')
        profile = profile[0]
        user = profile.user
        try:
            project = Project.objects.filter(head=user)
        except Project.DoesNotExist:
            no_project = True
        profile_data = model_to_dict(profile)
        user_data = model_to_dict(user)
        if no_project:
            return JsonResponse({
                'name': profile_data['name'],
                'role': profile_data['role'],
                'dept': profile_data['dept'],
                'email': user_data['email'],
                'is_staff': user_data['is_staff'],
                'image': str(user_data['image']),
                'projects': []
            })

        for cur_project in project:
            project_data = model_to_dict(cur_project)
            try:
                pmr = ProjectMemberRelationship.objects.filter(project__head=user)
            except ProjectMemberRelationship.DoesNotExist:
                no_scholars = True
            if no_scholars:
                project_data['scholars'] = []
                projects.append(project_data)
            else:
                scholars_profile = []
                for x in pmr:
                    try:
                        cur_profile = Profile.objects.filter(user=x.user)
                    except Profile.DoesNotExist:
                        return error_response('profile does not exist')
                    cur_profile = cur_profile[0]
                    cur_scholar_data = cur_profile.user
                    cur_scholar_data = model_to_dict(cur_scholar_data)
                    cur_profile = model_to_dict(cur_profile)
                    scholars_profile.append({
                        'name': cur_profile['name'],
                        'role': cur_profile['role'],
                        'dept': cur_profile['dept'],
                        'email': cur_scholar_data['email'],
                        'is_staff': cur_scholar_data['is_staff'],
                        'image': str(cur_scholar_data['image'])
                    })
                project_data['scholars'] = scholars_profile
                projects.append(project_data)
        
        return JsonResponse({
            'name': profile_data['name'],
            'role': profile_data['role'],
            'dept': profile_data['dept'],
            'email': user_data['email'],
            'is_staff': user_data['is_staff'],
            'image': str(user_data['image']),
            'projects': projects
        })

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdmin, name='dispatch')
class AssignRoles(View):
    """
    pass an user, project and respective role to be updated
    1-View, 2-Write, 3-Edit, 4-Admin
    """
    def post(self, req):
        user_id = req.POST.get('user_id')
        project_id = req.POST.get('project_id')
        role = req.POST.get('role')
        try:
            user = User.objects.filter(id=user_id)
        except User.DoesNotExist:
            return error_response('user does not exist')
        try:
            project = Project.objects.filter(id=project_id)
        except Project.DoesNotExist:
            return error_response('project does not exist')
        try:
            pmp = ProjectMemberPrivilege.objects.filter(code=role)
        except ProjectMemberPrivilege.DoesNotExist:
            return error_response('projectmemberprivilege does not exist')
        try:
            pmr = ProjectMemberRelationship.objects.get(project=project[0],user=user[0])
        except ProjectMemberRelationship.DoesNotExist:
            return error_response('projectmemberrelationship does not exist')
        
        pmr.privilege = pmp[0]
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
        user_id = req.POST.get('user_id')
        project_id = req.POST.get('project_id')
        role = req.POST.get('role')
        try:
            user = User.objects.filter(id=user_id)
        except User.DoesNotExist:
            return error_response('user does not exist !')
        try:
            project = Project.objects.filter(id=project_id)
        except Project.DoesNotExist:
            return error_response('project does not exist !')
        try:
            pmp = ProjectMemberPrivilege.objects.filter(code=role)
        except ProjectMemberPrivilege.DoesNotExist:
            return error_response('projectmemberprivilege does not exist !')
        
        if not ProjectMemberRelationship.objects.filter(user=user[0],project=project[0]).exists():
            pmr = ProjectMemberRelationship.objects.create(project=project[0],user=user[0],privilege=pmp[0])
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
