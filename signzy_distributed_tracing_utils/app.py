from functools import wraps
import asyncio
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode
from signzy_distributed_tracing_utils.config.TraceConfig import TraceConfig


# Initialize tracing function
def instrument(app):
    config = TraceConfig()
    if not config.enable_tracing:
        print("Tracing is disabled.")
        return
    
    if not config.tracing_endpoint:
        raise Exception("Tracing endpoint not provided.")

    if not config.trace_service_name:
        raise Exception("Trace service name not provided.")

    # Set up the tracer provider and processor
    trace.set_tracer_provider(TracerProvider(resource=Resource.create(
        attributes={"service.name": config.trace_service_name})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=config.tracing_endpoint))
    )
    # Instrumentations
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    print("Tracing is enabled ")



# Function level decorator for tracing
def instrument_with_tracing(operation_name=None, span_attrs=None):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not TraceConfig().enable_tracing:
                    return await func(*args, **kwargs)

                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span(operation_name or func.__name__, attributes=span_attrs) as span:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not TraceConfig().enable_tracing:
                    return func(*args, **kwargs)

                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span(operation_name or func.__name__, attributes=span_attrs) as span:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return sync_wrapper
    return decorator



