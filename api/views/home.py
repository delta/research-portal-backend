from api.models import AreaOfResearch, Department, Labs, COE
from django.views.generic import View
from django.http import HttpResponse
from api.decorators.response import JsonResponseDec
from django.utils.decorators import method_decorator
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
class AllDepartments(View):
    """
    Return all departments
    short_name and name
    """
    def get(self, req):
        departments = Department.objects.all()
        return {
            'data': list_to_dict(departments)
        }

@method_decorator(JsonResponseDec, name='dispatch') 
class AllAor(View):
    """
    Return all Areas of Research
    short_name and name
    """
    def get(self, req):
        aors = AreaOfResearch.objects.all()
        return {
            'data': list_to_dict(aors)
        }

@method_decorator(JsonResponseDec, name='dispatch') 
class AllCenters(View):
    """
    Return all Labs
    """
    def get(self, req):
        labs = Labs.objects.all()
        return {
            'data': list_to_dict(labs)
        }

@method_decorator(JsonResponseDec, name='dispatch')
class AllCoe(View):
    """
    Return all Centers of Excellence
    """
    def get(self, req):
        coe = COE.objects.all()
        return {
            'data': list_to_dict(coe)
        }