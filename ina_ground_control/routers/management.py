"""
Module for API health check endpoint.

This module provides a simple FastAPI-based health check endpoint that is primarily
used to verify the service's availability and proper functioning. It's commonly used
in containerized applications for purposes such as Docker orchestration and monitoring.

Classes:
    HealthCheck: Response model for the health check API.

Routes:
    GET /management/health: Returns the health status of the API service.
"""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest
from pydantic import BaseModel

from ina_ground_control import get_application_version, logger, settings


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"
    service_name: str
    version: str


router = APIRouter(tags=["management"])


@router.get(
    "/management/health",
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(
        service_name=settings.application,
        version=get_application_version(),
        status="OK",
    )


@router.get(
    "/management/metrics",
    summary="Metrics",
    response_description="Prometheus metrics in plain text format.",
)
def get_health_metrics() -> PlainTextResponse:
    """
    ## Fetch OpenTelemetry Metrics
    The `/management/metrics` endpoint exposes telemetry metrics that can be consumed
    by Prometheus or other monitoring systems for observability purposes.

    Logs errors in case of unexpected issues while generating metrics.

    Returns:
        PlainTextResponse: The Prometheus-compliant telemetry metrics in plain text format.
    """
    logger.info("Received request to fetch health metrics.")
    try:
        # Generate Prometheus metrics
        logger.info("Generating Prometheus OpenTelemetry metrics.")
        metrics = generate_latest()
        # Log successful metric generation
        logger.info("Successfully generated Prometheus metrics.")
        return PlainTextResponse(content=metrics)
    except Exception as e:
        # Log and handle any unexpected exceptions
        error_message = "Failed to fetch health metrics due to an unexpected error."
        logger.error("%s Details: %s", error_message, str(e))
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_message
        ) from e
