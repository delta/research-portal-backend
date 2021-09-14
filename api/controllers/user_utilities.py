from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email
from django.contrib.sessions.models import Session
from api.models import User
import logging

logger = logging.getLogger(__name__)

def validate_email(email):
    try:
        _validate_email(email)
        return True
    except ValidationError:
        return False

def register_user(email, name, password, is_staff, uploaded_file_url,department):
    
    user = User.objects.create_user(email=email,
                                    name=name,
                                    password=password,
                                    is_staff=is_staff,
                                    image=uploaded_file_url,
                                    is_verified=1,
                                    dept=department
                                    )
    user.save()

    logger.info('{} User registration successful'.format(email))
    return "Registration successful"

def remove_existing_sessions(user_id):
    """
    Removes sessions on other devices for the giver user_id
    """
    sessions = Session.objects.all()

    for session in sessions:
        data = session.get_decoded()
        if data.get('user_id', -1) == user_id:
            # Already a session exist, delete it
            session.delete()
    logger.info('User(pk={}) Existing sessions deleted'.format(user_id))
    return

def send_reset_pass_link(user):
    """
    Sends a reset password link to the user's email
    """
    pass
