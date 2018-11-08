from rest_framework.exceptions import APIException


class ProfileDoesNOtExist(APIException):
    status_code = 400
    default_detail = 'The requested profile does not exist.'
