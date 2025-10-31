import os

from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = "practices"  # Changed from practices-service for consistency perhaps


def setup_opentelemetry_sdk():
    """Configures the OpenTelemetry SDK with an OTLP exporter.

    The OTLP endpoint can be configured via the OTEL_EXPORTER_OTLP_ENDPOINT environment variable.
    Defaults to localhost:4317 for local development.
    """
    try:
        resource = Resource(attributes={"service.name": SERVICE_NAME})

        default_otlp_endpoint = "localhost:4317"  # Ensure no scheme
        otlp_endpoint_env = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")

        if otlp_endpoint_env:
            otlp_endpoint = otlp_endpoint_env
            # If an explicit endpoint is provided via env var,
            # assume it's for container-to-container communication (e.g., "otel-collector:4317")
            # and should be insecure unless it's something other than the typical collector name.
            # A more robust solution might inspect the otlp_endpoint string for "localhost"
            # or have a separate OTEL_EXPORTER_OTLP_INSECURE env var.
            # For now, if it's set, assume it's the docker internal one and should be insecure.
            insecure_connection = True
        else:
            otlp_endpoint = default_otlp_endpoint
            # When defaulting to localhost, it's connecting from host to container,
            # and the default collector gRPC is insecure.
            insecure_connection = True

        logger.info(
            f"OTLP Exporter will target: {otlp_endpoint}, Insecure: {insecure_connection} (from backend/practices/practices/monitoring)"
        )

        # The OTLPSpanExporter endpoint should be host:port, or include a scheme if secure.
        # For insecure gRPC, host:port is correct.
        # If using http/otlp, it would be http://host:port/v1/traces
        # The OTLPSpanExporter handles gRPC, so host:port is generally what's needed.
        # If the endpoint itself contains "http://" or "https://", the library might handle it,
        # but for clarity and typical gRPC usage, we'll strip it if `insecure_connection` is True.

        exporter_target_endpoint = otlp_endpoint
        if insecure_connection and otlp_endpoint.startswith("http://"):
            exporter_target_endpoint = otlp_endpoint.replace("http://", "")
        elif not insecure_connection and otlp_endpoint.startswith("https://"):  # For future if secure is used
            exporter_target_endpoint = otlp_endpoint.replace("https://", "")

        otlp_exporter = OTLPSpanExporter(
            endpoint=exporter_target_endpoint, insecure=insecure_connection  # Use the processed endpoint
        )

        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)

        logger.info(f"OpenTelemetry SDK configured for service: {SERVICE_NAME} with OTLP gRPC exporter.")

    except Exception as e:
        logger.exception(f"Failed to configure OpenTelemetry SDK: {e}")
