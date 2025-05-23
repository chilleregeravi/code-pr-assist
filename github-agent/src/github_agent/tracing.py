try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc._trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    TRACING_AVAILABLE = True
except ImportError:
    # Fallback for testing or when OpenTelemetry is not properly configured
    TRACING_AVAILABLE = False


def setup_tracing(service_name: str = "github-agent"):
    """Setup OpenTelemetry tracing if available."""
    if not TRACING_AVAILABLE:
        print(f"Warning: OpenTelemetry tracing not available for {service_name}")
        return

    try:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception as e:
        print(f"Warning: Failed to setup tracing for {service_name}: {e}")
