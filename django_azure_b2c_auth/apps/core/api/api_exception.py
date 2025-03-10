from rest_framework.exceptions import APIException


class B2CContractNotRespectedException(APIException):
    status_code = 400
    default_detail = "It seems something is missing to accomplish the task"


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"
