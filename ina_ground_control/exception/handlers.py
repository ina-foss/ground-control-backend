import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from ina_ground_control.exception.exceptions import (
    GroundControlException,
    UnexpectedError,
    GroundControlRequestValidationError,
)

async def default_exception_handler(request: Request, exception: Exception):
    """Handles exceptions globally in the Ground Control project."""
    extra = {}
    try:
        if isinstance(exception, RequestValidationError):
            exception = GroundControlRequestValidationError()
        elif not isinstance(exception, GroundControlException):
            exception = UnexpectedError()
    except Exception as e:
        logging.getLogger("errors").error("Error handling exception", exc_info=True)
        exception = UnexpectedError()

    short_message = exception.formatted_str()
    extra.update({
        "code": getattr(exception, "code", "UNKNOWN_ERROR"),
        "uuid": getattr(exception, "uuid", None),
        "http_status": getattr(exception, "http_status", 500),
        "login": request.headers.get("oidc-login", None),
    })

    logging.getLogger("errors").error(short_message, extra=extra, exc_info=True)

    return JSONResponse(
        status_code=exception.http_status,
        content={
            "code": exception.code,
            "uuid": exception.uuid,
            "message": exception.formatted_str(),
            "raw_message": exception.message
        }
    )
