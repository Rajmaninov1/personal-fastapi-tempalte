from fastapi import status


class BaseAPIException(Exception):
    pass


class BaseAPIHTTPException(BaseAPIException):
    """Base class for all API exceptions"""
    default_message: str
    example_message: str
    http_status_code: int

    def get_openapi_response(self) -> list:
        return [[self.http_status_code, {'description': self.example_message}]]

    def __init__(self, *args) -> None:
        if args:
            super().__init__(self.default_message.format(*args))
        else:
            super().__init__(self.default_message)


class DeprecatedEndpoint(BaseAPIException):
    http_status_code = 299
    default_message = 'Deprecated'
    example_message = default_message


class UserNotFound(BaseAPIHTTPException):
    http_status_code = status.HTTP_404_NOT_FOUND
    default_message = 'User not found'
    example_message = default_message
