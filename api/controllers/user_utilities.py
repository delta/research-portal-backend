from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email
from django.contrib.sessions.models import Session
from api.models import User
import logging, os, time
import sendgrid
from string import ascii_letters, digits
from random import choice
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get('API_BASE_URL')
FRONTEND_BASE_URL = os.environ.get('API_BASE_URL')

def validate_email(email):
    try:
        _validate_email(email)
        return True
    except ValidationError:
        return False

def register_user(email, name, password, is_staff, uploaded_file_url,auth_token):
    
    user = User.objects.create_user(email=email,
                                    name=name,
                                    password=password,
                                    is_staff=is_staff,
                                    image=uploaded_file_url,
                                    token=auth_token,
                                    is_verified=1)
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
    act_url = ('{API_BASE_URL}/user/verify_email/?token={auth_token}').format(
                    API_BASE_URL=os.environ.get('API_BASE_URL'),
                    auth_token=user.token
                )
    sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('APP_NOREPLY_EMAIL'))
    to_email = To(user.email)
    subject = "Verify-Email : Research Portal"
    html_content = """
    <html>
        <body>
            <p>
                Hello, <br>
                <br>
                Please click on the following link to verify your email address
                <br>
                <a href="{act_url}">{act_url}</a>
                <br>
                <br>
                Regards, <br>
                Research Portal
            </p>
        </body>
    </html>
    """.format(act_url=act_url)
    content = Content("text/html", html_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.send(mail)
    return response

# Function to send a reset password link mail to the user's email address
def send_reset_pass_link(user):
    """
    Sends a reset password link to the user's email using sendgrid
    """
    # Handle this by showing a form at that url in the frontend and sending a post request with the new password to the backend route to update password
    act_url = ('{FRONTEND_BASE_URL}/user/verify_email/?token={auth_token}').format(
                FRONTEND_BASE_URL=FRONTEND_BASE_URL,
                auth_token=user.token
            )
    sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('APP_NOREPLY_EMAIL'))
    to_email = To(user.email)
    subject = "Password-reset : Research Portal"
    html_content = """
        <html>
            <body>
                <p>
                Hello,<br>
                <br>
                You have requested to reset your password for the Research Portal.<br>
                <br>
                Please click on the link below to reset your password.<br>
                <br>
                <a href="{act_url}">Reset Password</a><br>
                <br>
                If you did not request to reset your password, please ignore this email.<br>
                <br>
                Thank you,<br>
                <br>
                Research Portal Team
                </p>
            </body>
        </html>
    """.format(act_url=act_url)
    content = Content("text/html", html_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.send(mail)
    return response