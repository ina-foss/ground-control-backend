"""
This module provides a custom exception handler for FastAPI applications, enabling
structured error responses and unified logging for various exception types.

"""

import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from ina_ground_control.exception.exceptions import (
    GroundControlException,
    GroundControlRequestValidationError,
    UnexpectedError,
)


async def default_exception_handler(request: Request, exception: Exception):
    """
    Handles custom exception behavior for FastAPI applications by processing the exception
    into a structured response. It also logs the exception details with additional context
    information including the HTTP status code, error code, UUID, and user login.

    The function specifically maps FastAPI validation errors and general exceptions to
    application-specific exceptions (`GroundControlRequestValidationError` and
    `UnexpectedError`) to unify error handling and logging. If an error occurs during
    exception processing, it defaults to returning a general `UnexpectedError`.

    :param request: The HTTP request object from FastAPI, containing request-specific data.
    :type request: Request
    :param exception: The exception instance to be processed into an error response.
    :type exception: Exception
    :return: A JSON response containing the HTTP status, formatted error details, error
        code, UUID, and raw error message.
    :rtype: JSONResponse
    """
    extra = {}
    try:
        if isinstance(exception, RequestValidationError):
            exception = GroundControlRequestValidationError()
        elif not isinstance(exception, GroundControlException):
            exception = UnexpectedError()
    except Exception as e:
        logging.getLogger("errors").error("Error handling exception: %s", str(e))
        exception = UnexpectedError()

    short_message = exception.formatted_str()
    extra.update(
        {
            "code": getattr(exception, "code", "UNKNOWN_ERROR"),
            "uuid": getattr(exception, "uuid", None),
            "http_status": getattr(exception, "http_status", 500),
            "login": request.headers.get("oidc-login", None),
        }
    )

    logging.getLogger("errors").error(short_message, extra=extra, exc_info=True)

    return JSONResponse(
        status_code=exception.http_status,
        content={
            "code": exception.code,
            "uuid": exception.uuid,
            "message": exception.formatted_str(),
            "raw_message": exception.message,
        },
    )
