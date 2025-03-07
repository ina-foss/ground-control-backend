"""
Module for handling OpenTelemetry instrumentation with FastAPI.

This module defines the `TelemetryService` class, which provides functionality
to set up and manage OpenTelemetry tracing and metrics in a FastAPI application.
"""

from fastapi import FastAPI, Request
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


class TelemetryService:
    """
    Service for handling OpenTelemetry instrumentation in FastAPI.
    """

    def __init__(self, application: FastAPI):
        self.application = application
        self._setup_tracing()
        self._setup_metrics()

    def _setup_tracing(self):
        """Setup OpenTelemetry Tracing."""
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        FastAPIInstrumentor.instrument_app(self.application)

    def _setup_metrics(self):
        """Setup OpenTelemetry Metrics."""
        prometheus_reader = PrometheusMetricReader()
        meter_provider = MeterProvider(metric_readers=[prometheus_reader])
        set_meter_provider(meter_provider)

        # Store the Prometheus reader reference (useful if integration is needed elsewhere)
        self.prometheus_reader = prometheus_reader

        # Meter and metric objects
        self.meter = get_meter_provider().get_meter("fastapi_otlp")
        self.request_counter = self.meter.create_counter(
            "http_requests_total", "Total HTTP Requests"
        )
        self.request_latency = self.meter.create_histogram(
            "http_request_duration_seconds", "Request Latency in Seconds"
        )

    def record_metrics(self, request: Request, response_time: float, status_code: int):
        """Record request metrics."""
        self.request_counter.add(
            1, {"method": request.method, "endpoint": request.url.path, "status_code": str(status_code)}
        )
        self.request_latency.record(
            response_time, {"method": request.method, "endpoint": request.url.path}
        )
