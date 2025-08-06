"""
telemetry_service.py
This module provides a telemetry service to instrument FastAPI with OpenTelemetry.
"""
import os

from fastapi import FastAPI, Request
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from ina_ground_control import logger


class TelemetryService:
    """
    Service for handling OpenTelemetry instrumentation in FastAPI.
    """

    def __init__(self, application: FastAPI, sql_alchemy_engine):
        self.application = application
        # Fetch Kubernetes metadata from environment variables
        self.resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: 'toolbox-ia-backend',
            ResourceAttributes.K8S_NAMESPACE_NAME: os.getenv('KUBERNETES_NAMESPACE', 'unknown-namespace'),
            ResourceAttributes.K8S_POD_NAME: os.getenv('KUBERNETES_POD_NAME', 'unknown-pod'),
            ResourceAttributes.K8S_POD_UID: os.getenv('KUBERNETES_POD_UID', 'unknown-node'),
            ResourceAttributes.K8S_NODE_NAME: os.getenv('KUBE_NODE_NAME', 'unknown-node')
        })
        self._setup_metrics()
        if sql_alchemy_engine is not None:
            SQLAlchemyInstrumentor().instrument(engine=sql_alchemy_engine)
        else:
            logger.warning('SQLAlchemyInstrumentor is not initialize')
        FastAPIInstrumentor.instrument_app(self.application, excluded_urls='/management/metrics')

    def _setup_metrics(self):
        """Setup OpenTelemetry Metrics."""
        prometheus_reader = PrometheusMetricReader()
        meter_provider = MeterProvider(metric_readers=[prometheus_reader], resource=self.resource)
        # Store the Prometheus reader reference (useful if integration is needed elsewhere)
        self.prometheus_reader = prometheus_reader
        # Meter and metric objects
        self.meter = get_meter_provider().get_meter('ToolboxIA')
        self.request_counter = self.meter.create_counter(
            'http_requests_total', 'Total HTTP Requests'
        )
        self.request_latency = self.meter.create_histogram(
            'http_request_duration_seconds', 'Request Latency in Seconds'
        )
        set_meter_provider(meter_provider)

    def record_metrics(self, request: Request, response_time: float, status_code: int):
        """Record request metrics."""
        self.request_counter.add(
            1, {'method': request.method, 'endpoint': request.url.path, 'status_code': str(status_code)}
        )
        self.request_latency.record(
            response_time, {'method': request.method, 'endpoint': request.url.path}
        )
