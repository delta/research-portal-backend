from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email
from django.contrib.sessions.models import Session
from api.models import User
import logging, os, time
from string import ascii_letters, digits
from random import choice
from api.controllers.email_utilities import send_email, get_message_with_headers
from api.helpers.email_helpers import get_html

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get('BACKEND_ROOT_APP_URL') + '/api'
FRONTEND_BASE_URL = os.environ.get('API_BASE_URL')

def validate_email(email):
    try:
        _validate_email(email)
        return True
    except ValidationError:
        return False

def register_user(email, name, password, is_staff, uploaded_file_url, department, auth_token):
    
    user = User.objects.create_user(email=email,
                                    name=name,
                                    password=password,
                                    is_staff=is_staff,
                                    image=uploaded_file_url,
                                    is_verified=0,
                                    dept=department,
                                    token=auth_token,
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

# Function to generate an auth_token for the verification and password reset things
def generate_auth_token(length=30):
    '''
    Generates a random string of the given length containing ascii letters and
    digits.
    Args:
        length(int)[optional] : Describing the length of the required auth token
    Returns:
        auth_token : A random string of given length
    '''

    auth_token_domain = ascii_letters + digits
    auth_token = ''.join(choice(auth_token_domain) for i in range(length))
    auth_token = auth_token + str(time.time())

    return auth_token

# Function to send a verification email to the user's email address
def send_verify_mail_link(user):
    """
    Sends a verification mail to the user's email address.
    Args:
        user(User) : The user for whom the verification mail is to be sent
    """
    recepients = [user.email]
    msg = get_message_with_headers()
    msg['Subject'] = "Please verify your account"
    msg['To'] = ', '.join(recepients)
    root_url = os.environ.get('BACKEND_ROOT_APP_URL')
    msg.set_content(f'''Please click the following link to verify your email: https://research.nitt.edu/api/user/verify_email/?auth_token={user.token}''')

    msg.add_alternative(get_html(
                        content=f'''Please click the following link to verify your email:''',
                                link=f'{root_url}/api/user/verify_email/?auth_token={user.token}',
                                linkText="Click Here"
                        ), subtype="html")
    print(f'{root_url}/api/user/verify_email/?auth_token={user.token}')
    return send_email(msg)

# Function to send a reset password link mail to the user's email address
def send_reset_pass_link(user):
    """
    Sends a reset password link to the user's email using sendgrid
    """
    # Handle this by showing a form at that url in the frontend and sending a post request with the new password to the backend route to update password
    recepients = [user.email]
    msg = get_message_with_headers()
    msg['Subject'] = "Link to reset your password"
    msg['To'] = ', '.join(recepients)
    root_url = os.environ.get('BACKEND_ROOT_APP_URL')
    msg.set_content(f'''Please click the following link to reset your password: {root_url}/api/user/reset-password/?auth_token={user.token}''')

    msg.add_alternative(get_html(
                        content=f'''Please click the following link to reset your password:''',
                                link=f'{root_url}/api/user/reset-password/?auth_token={user.token}',
                                linkText="Click Here"
                        ), subtype="html")

    return send_email(msg)
