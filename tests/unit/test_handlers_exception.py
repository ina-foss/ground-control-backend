import json

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError

from ina_ground_control.exception.exceptions import (
    GroundControlException,
    GroundControlRequestValidationError,
    UnexpectedError,
)
from ina_ground_control.exception.handlers import default_exception_handler


@pytest.mark.asyncio
async def test_default_exception_handler_with_request_validation_error():
    request = Request(scope={"type": "http", "headers": []})
    exc = RequestValidationError([])
    response = await default_exception_handler(request, exc)

    body = json.loads(response.body.decode())
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert "Invalid request parameters" in body["message"]


@pytest.mark.asyncio
async def test_default_exception_handler_with_unexpected_exception():
    request = Request(scope={"type": "http", "headers": []})
    exc = Exception("Some error")
    response = await default_exception_handler(request, exc)

    body = json.loads(response.body.decode())
    assert response.status_code == 500
    assert body["code"] == "INTERNAL_SERVER_ERROR"
    assert "An unexpected error occurred" in body["message"]


@pytest.mark.asyncio
async def test_default_exception_handler_with_ground_control_exception():
    from ina_ground_control.exception.exceptions import ErrorCode

    request = Request(scope={"type": "http", "headers": []})

    # Create a GroundControlException with a proper ErrorCode
    exc = GroundControlException(error=ErrorCode.INTERNAL_SERVER_ERROR)
    response = await default_exception_handler(request, exc)

    body = json.loads(response.body.decode())
    assert response.status_code == 500
    assert body["code"] == "INTERNAL_SERVER_ERROR"
    assert "An unexpected error occurred" in body["message"]


@pytest.mark.asyncio
async def test_default_exception_handler_error_during_handling(monkeypatch):
    request = Request(scope={"type": "http", "headers": []})

    # Patch GroundControlRequestValidationError to raise an exception during init
    def mock_init(self):
        raise Exception("init error")

    monkeypatch.setattr(
        "ina_ground_control.exception.exceptions.GroundControlRequestValidationError.__init__",
        mock_init,
    )

    exc = RequestValidationError([])
    response = await default_exception_handler(request, exc)

    body = json.loads(response.body.decode())
    assert response.status_code == 500
    assert body["code"] == "INTERNAL_SERVER_ERROR"
    assert "An unexpected error occurred" in body["message"]
