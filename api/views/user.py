from django.contrib import auth
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.views.generic import View
from api.controllers.response_format import error_response
from django.contrib.auth import authenticate, login
from api.controllers.user_utilities import *
from api.models import User, Department
from api.decorators.response import JsonResponseDec
from django.utils.decorators import method_decorator
from api.decorators.permissions import IsStaffDec, CheckAccessPrivilegeDec, CheckAdminLevelDec
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import redirect
import logging
import json
import os

logger = logging.getLogger(__name__)


def list_to_dict(items):
    '''
    Converts a given QuerySet into a list of dictionaries
    '''
    converted = []
    for item in items:
        converted.append(model_to_dict(item))
    return converted


@method_decorator(JsonResponseDec, name='dispatch')
class LoginFormView(View):
    def post(self, req):
        """
        Logs in the user and sets session
        """
        user = json.loads(req.body)
        email = user['email']
        password = user['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("User does not exist")

        if user.is_verified:
            user = authenticate(username=email, password=password)
        else:
            logger.info('User(email={}) Verification pending'.format(email))
            return error_response("Email verification pending. Please check your inbox to activate your account")

        if user is not None:
            remove_existing_sessions(user.id)
            login(req, user)
            req.session['user_id'] = user.id
            response = {'email': user.email, 'name': user.name, }
            logger.info('{} Login successful'.format(user))
            return response
        else:
            logger.info('User(email={}) Password incorrect'.format(email))
            return error_response("User password incorrect")


@method_decorator(JsonResponseDec, name='dispatch')
class LogoutView(View):
    def post(self, req):
        """
        Logs out user by deleting his session
        """
        user = req.session.get('user_id')

        if user is not None:
            del req.session['user_id']
            logger.info('{} Logged out successfully'.format(user))
            return "Logged out successfully!"
        else:
            logger.info('{} Logout error'.format(user))
            return error_response("Logout error!")


@method_decorator(JsonResponseDec, name='dispatch')
class RegisterFormView(View):
    def post(self, req):
        """
        If the credentials are in proper format and email doesn't already exist, register a user
        """
        email = req.POST.get('email')
        password = req.POST.get('password')
        name = req.POST.get('name')
        is_staff = True
        department = req.POST.get('department')
        # get department with short_name as department
        try:
            department = Department.objects.get(short_name=department)
        except Department.DoesNotExist:
            return error_response("Department does not exist")

        myfile = req.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)

        if "@nitt.edu" not in email:
            return error_response("Please use webmail")

        if validate_email(email) and len(password) >= 8 and name is not None:
            if email.split("@")[0].isnumeric():
                is_staff = False
            if not User.objects.filter(email=email).exists():
                auth_token = generate_auth_token(50)
                register_user(email, name, password, is_staff, uploaded_file_url, department, auth_token)
                user = User.objects.get(email=email)
                mail_success = send_verify_mail_link(user)
                logger.info('User(webmail={}) Registration successful! Verification email sent'.format(email))
                if mail_success:
                    return "Verification email has been sent to " + email
                else:
                    return error_response("Error sending verification link to " + email)
            else:
                logger.info(
                    'User(webmail={}) Account already exists'.format(email))
                return error_response("An account already exists under the webmail address")
        else:
            logger.info('email={} Invalid user details')
            return error_response("Invalid user details")

@method_decorator(JsonResponseDec, name='dispatch')
class ResetPassRequest(View):
    def post(self, req):
        """Get email from post request.
            Check if the user exists and is verified.
            Then send reset password link to user"""
        data = json.loads(req.body)
        email = data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("User does not exist")

        if user.is_verified:
            send_reset_pass_link(user)
            logger.info(
                'User(email={}) Password reset link sent'.format(email))
            return "Password reset link sent!"
        else:
            logger.info('User(email={}) Verification pending'.format(email))
            return error_response("Email verification pending. Please check your inbox to activate your account")

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsStaffDec, name='dispatch')
class GetIsStaff(View):
    """
        Returns the privilege of a user
    """

    def get(self, req):
        return {
            'data': req.is_staff
        }

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAdminLevelDec, name='dispatch')
class GetAdminLevel(View):
    """
        Returns the admin_level of a user
    """

    def get(self, req):
        return {
            'data': req.admin_level
        }

@method_decorator(JsonResponseDec, name='dispatch')
class ResetPassUpdate(View):
    def post(self, req):
        data = json.loads(req.body)
        new_pass = data['new_password']
        token = data['token']

        try:
            user = User.objects.get(token=token)
        except:
            logger.info('Token({}): Invalid token'.format(token))
            return error_response("Invalid Token")
        # TODO - check password conditions if any and throw error if not met
        user.set_password(new_pass)
        new_token = generate_auth_token(50)
        user.token = new_token
        user.save()
        logger.info('{} Password reset successful'.format(user))
        return "Password successfully reset!"


class VerifyEmail(View):
    def get(self,req):
        """
        Verify the user by setting is_verified to True
        """
        auth_token = req.GET.get('auth_token')
        print(auth_token)
        try:
            user = User.objects.get(token=auth_token)
        except User.DoesNotExist:
            return JsonResponse({
                'status_code': 400,
                'data': "Invalid token",
            })
        print(user.is_verified)
        if user.is_verified:
            return JsonResponse({
                'status_code': 400,
                'data': "User already verified",
            })
        else:
            user.is_verified = True
            new_token = generate_auth_token(50)
            user.token = new_token
            user.save()
            logger.info('User(email={}) Verified successfully'.format(user.email))
            return redirect(os.environ.get('FRONTEND_BASE_URL') + 'login')
