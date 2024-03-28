# Configuration class using properties
import os 
from signzy_distributed_tracing_utils.constants.env import SIGNZY_ENABLE_TRACING, SIGNZY_TRACE_SERVICE_NAME, SIGNZY_TRACING_ENDPOINT

class TraceConfig:
    @property
    def enable_tracing(self):
        return os.getenv(SIGNZY_ENABLE_TRACING, "false").lower() == "true"

    @property
    def tracing_endpoint(self):
        return os.getenv(SIGNZY_TRACING_ENDPOINT)

    @property
    def trace_service_name(self):
        return os.getenv(SIGNZY_TRACE_SERVICE_NAME)
