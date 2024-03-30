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
from distributed_tracing_utils.constants.common import FALCON, FASTAPI, FLASK
from opentelemetry.trace import Status, StatusCode
from distributed_tracing_utils.config.TraceConfig import TraceConfig


class InstrumentorInterface:
    def instrument_framework(self, app):
        raise NotImplementedError
    

class FastAPIInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)

class FlaskInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        FlaskInstrumentor().instrument_app(app)

class FalconInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.falcon import FalconInstrumentor
        FalconInstrumentor().instrument()        


def initialize_instrumentor(framework, app):
    instrumentor = None
    if framework == FASTAPI:
        instrumentor = FastAPIInstrumentor()
    elif framework == FLASK:
        instrumentor = FlaskInstrumentor()
    elif framework == FALCON:
        instrumentor = FalconInstrumentor()
    else:
        raise ValueError(f"Unsupported framework {framework}")

    if instrumentor:
        instrumentor.instrument_framework(app)


# Initialize tracing function
def instrument(app=None, framework=FASTAPI):
    """
       Main action that enables auto instrumentation
       params : 
       app : the instance of the fastapi, flask ,falcon application
       framework: the name of the framework which needs to be instrumented 
    """
    config = TraceConfig()
    if not config.enable_tracing:
        print("Tracing is disabled.")
        return

    if not config.tracing_endpoint:
        raise Exception("Tracing endpoint not provided.")

    if not config.trace_service_name:
        raise Exception("Trace service name not provided.")

  
    provider = TracerProvider(resource=Resource.create(attributes={
        "service.name": config.trace_service_name
    }))
    # span processor
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=config.tracing_endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    initialize_instrumentor(framework, app)
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    print("Tracing is enabled ")





def instrument_with_tracing(operation_name=None, span_attrs=None):
    """
    decorator for applying instrumentation on function (supports both async and sync functions)
    params:
    operation_name(optional) : name you want to give to the function(if not provided default function name will be used)
    span_attrs(optional) : custom attributes you want to give to the function
    """
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




