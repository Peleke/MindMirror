from fastapi import FastAPI
from loguru import logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator


def setup_prometheus(app: FastAPI):
    """Sets up Prometheus instrumentation for the FastAPI app."""
    print("[DEBUG] Entering setup_prometheus (backend/practices/practices/monitoring)")
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus instrumentation configured and /metrics endpoint exposed.")
    print("[DEBUG] Exiting setup_prometheus (backend/practices/practices/monitoring)")


def setup_opentelemetry(app: FastAPI):
    """Sets up OpenTelemetry FastAPI instrumentation."""
    print("[DEBUG] Entering setup_opentelemetry (backend/practices/practices/monitoring)")
    # Basic instrumentation. Exporter configuration will be separate.
    # If you have specific OTel SDK configurations (e.g., resource attributes, tracer provider),
    # they should be done before or around this call, typically in your app's entry point.
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry FastAPI instrumentation enabled.")
    print("[DEBUG] Exiting setup_opentelemetry (backend/practices/practices/monitoring)")
