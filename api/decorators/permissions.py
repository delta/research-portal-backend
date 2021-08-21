import logging
from django.contrib.sessions.models import Session
from api.controllers.response_format import unauthorized_response
from api.models import User
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
