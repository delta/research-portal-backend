from django.views.generic import View
from django.forms.models import model_to_dict
from
from api.models import  User

class AllUsers(View):
    def get(self, req):
        users = User.objects.filter(is_staff=True)
        data = []
        for user in users:
            user = model_to_dict(user)
            data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'is_verified': user['is_verified'],
                'is_staff': user['is_staff'],

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
