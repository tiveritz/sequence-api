from rest_framework import status
from rest_framework.exceptions import APIException


class NotAValidStepType(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Given step type is not a valid step type'
