import logging
from opentelemetry import trace
from opentelemetry.trace import get_current_span

class TraceIdFormatter(logging.Formatter):
    """
    A formatter that enriches log records with trace ID information from the current OpenTelemetry span.
    """
    def format(self, record):
        """
        Adds trace ID to the log record before formatting the message.
        
        Args:
            record (logging.LogRecord): The log record to be formatted.
        
        Returns:
            str: The formatted log message including the trace ID.
        """
        current_span = get_current_span()
        trace_id = trace.format_trace_id(current_span.get_span_context().trace_id) if current_span else 'no-trace'
        record.trace_id = trace_id
        return super().format(record)


# Configure the logger upon module import
def _configure_logger(name):
    """
    Configures and returns a logger with a specific format that includes time, level,
    trace ID, and the log message.
    
    Args:
        name (str): The name of the logger, typically __name__ when used in modules.
        
    Returns:
        logging.Logger: The configured logger with trace ID integration.
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = TraceIdFormatter('%(asctime)s %(levelname)s [%(trace_id)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

# Automatically provide a logger object to the user
logger = _configure_logger("distributed_tracing_utils_logger")