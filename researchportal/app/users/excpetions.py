from rest_framework.exceptions import APIException

# We are hitting LDAP, for user profile.
# When profile is not found in LDAP, we can raise this error
class UserDoesNotExist(APIException):
    status_code = 400
    default_detail = "The requested user does not exist."
