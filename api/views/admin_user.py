from django.views.generic import View
from django.forms.models import model_to_dict
from django.http import JsonResponse
from api.models import  User
from django.utils.decorators import method_decorator
from api.decorators.response import JsonResponseDec
from django.db.models import Q

class AllUsers(View):
    def get(self, req):
        users = User.objects.filter(is_staff=True)
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

class Profile(View):
    def post(self, req):
        pass

class AssignRoles(View):
    def post(self, req):
        pass

class CreateTags(View):
    def post(self, req):
        pass

class AddMembers(View):
    def post(self, req):
        pass

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
