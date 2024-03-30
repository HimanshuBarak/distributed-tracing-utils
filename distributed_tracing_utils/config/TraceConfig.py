# Configuration class using properties
import os 
from distributed_tracing_utils.constants.env import ENABLE_TRACING, TRACE_SERVICE_NAME, TRACING_ENDPOINT

class TraceConfig:
    @property
    def enable_tracing(self):
        return os.getenv(ENABLE_TRACING, "false").lower() == "true"

    @property
    def tracing_endpoint(self):
        return os.getenv(TRACING_ENDPOINT)

    @property
    def trace_service_name(self):
        return os.getenv(TRACE_SERVICE_NAME)
