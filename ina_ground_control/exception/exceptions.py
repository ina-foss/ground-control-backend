import uuid
from enum import Enum
from fastapi.exceptions import RequestValidationError

from enum import Enum

class ErrorCode(Enum):
    INVALID_CREDENTIALS = ("INVALID_CREDENTIALS", "Invalid username or password", 401)
    PERMISSION_DENIED = ("PERMISSION_DENIED", "You do not have permission {permission} to {action} this resource", 403)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "Invalid request parameters", 422)
    INTERNAL_SERVER_ERROR = ("INTERNAL_SERVER_ERROR", "An unexpected error occurred", 500)
    # Generic errors with placeholders for custom messages
    RESOURCE_NOT_FOUND = ("RESOURCE_NOT_FOUND", "Failed to retrieve {resource} with: {id}", 404)
    GENERIC_CLIENT_ERROR = ("GENERIC_CLIENT_ERROR", "{details}", 400)
    GENERIC_OPERATION_FAILED = ("GENERIC_OPERATION_FAILED", "Failed to {action} {resource} with {id}", 500)
    # Business-Specific Errors

    def __init__(self, code, default_message, http_status):
        self.code = code
        self.default_message = default_message
        self.http_status = http_status

    def formatted_message(self, **kwargs):
        """
        Returns the default message if no kwargs are provided.
        If kwargs are provided, it formats the message dynamically.
        """
        try:
            return self.default_message.format(**kwargs)
        except KeyError:
            return self.default_message


class GroundControlException(Exception):
    """Base Exception for Ground Control."""

    def __init__(self, error: ErrorCode, **kwargs):
        self.code = error.code
        self.message = error.formatted_message(**kwargs)
        self.http_status = error.http_status
        self.uuid = str(uuid.uuid4())

    def formatted_str(self):
        return f"[{self.uuid}] {self.code}: {self.message}"


class UnexpectedError(GroundControlException):
    """Handles unexpected errors."""

    def __init__(self):
        super().__init__(ErrorCode.INTERNAL_SERVER_ERROR)


class GroundControlRequestValidationError(GroundControlException):
    """Handles request validation errors."""

    def __init__(self):
        super().__init__(ErrorCode.VALIDATION_ERROR)