# tests/unit/test_telemetry_service.py
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request

from ina_ground_control.services.telemetry_service import TelemetryService


@pytest.fixture
def fastapi_app():
    return FastAPI()


@pytest.fixture
def fake_request():
    req = Mock(spec=Request)
    req.method = "GET"
    req.url.path = "/test-endpoint"
    return req


def test_telemetry_service_initialization(fastapi_app):
    """Test that TelemetryService can be instantiated without a SQLAlchemy engine."""
    with patch(
        "ina_ground_control.services.telemetry_service.SQLAlchemyInstrumentor"
    ) as mock_sql:
        with patch(
            "ina_ground_control.services.telemetry_service.FastAPIInstrumentor"
        ) as mock_fastapi:
            service = TelemetryService(application=fastapi_app, sql_alchemy_engine=None)
            assert service.application == fastapi_app
            assert service.resource is not None
            assert service.prometheus_reader is not None
            assert service.meter is not None
            mock_sql().instrument.assert_not_called()
            mock_fastapi.instrument_app.assert_called_once_with(
                fastapi_app, excluded_urls="/management/metrics"
            )


def test_telemetry_service_with_sqlalchemy(fastapi_app):
    """Test that SQLAlchemyInstrumentor is called when engine is provided."""
    fake_engine = Mock()
    with patch(
        "ina_ground_control.services.telemetry_service.SQLAlchemyInstrumentor"
    ) as mock_sql:
        with patch(
            "ina_ground_control.services.telemetry_service.FastAPIInstrumentor"
        ) as mock_fastapi:
            service = TelemetryService(
                application=fastapi_app, sql_alchemy_engine=fake_engine
            )
            mock_sql().instrument.assert_called_once_with(engine=fake_engine)
            mock_fastapi.instrument_app.assert_called_once()


def test_record_metrics(fastapi_app, fake_request):
    """Test that record_metrics calls the counter and histogram methods."""
    service = TelemetryService(application=fastapi_app, sql_alchemy_engine=None)
    service.request_counter = Mock()
    service.request_latency = Mock()

    service.record_metrics(fake_request, response_time=0.123, status_code=200)

    service.request_counter.add.assert_called_once_with(
        1, {"method": "GET", "endpoint": "/test-endpoint", "status_code": "200"}
    )
    service.request_latency.record.assert_called_once_with(
        0.123, {"method": "GET", "endpoint": "/test-endpoint"}
    )
