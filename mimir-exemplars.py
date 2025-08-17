import random
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider, format_trace_id, get_tracer

otel_url = "10.152.183.152"
collector_endpoint = f"http://{otel_url}:4318/v1/metrics"

resource = Resource(attributes={
    SERVICE_NAME: "service",
    SERVICE_VERSION: "1.0.0"
})

otlp_exporter = OTLPMetricExporter(endpoint=collector_endpoint)
metric_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=5000)

meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("meter", "1.0.0")
metric_name = "demo_counter"
counter = meter.create_counter(metric_name, description="A placeholder counter metric")

# Set up and register the TracerProvider
tracer_provider = TracerProvider()
set_tracer_provider(tracer_provider)
tracer = tracer_provider.get_tracer("service")

# Create a span and record a metric within the span's context
with tracer.start_as_current_span("generate_metrics_span") as span:
    trace_id = span.get_span_context().trace_id
    trace_id_hex = format_trace_id(trace_id)
    print("Trace ID: %s", trace_id_hex)
    # Record metric — exemplar should be attached automatically
    counter.add(100)
