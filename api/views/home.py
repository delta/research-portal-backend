from django.views.generic import View
from django.http import HttpResponse

# example to get coding
class AllDepartments(View):
    def get(self, req):
        html = "<html><body>It is now 2pm</body></html>"
        return HttpResponse(html)
    
class AllAor(View):
    def get(self, req):
        pass

class AllCenters(View):
    def get(self, req):
        pass
