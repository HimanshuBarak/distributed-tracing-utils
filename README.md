# signzy-distributed-tracing-utils

This is the first version of signzy-distributed-tracing in python

Currently the following features are supported:

1. Auto Instrumentation for FastAPI , redis, http and pymongo
2. Manual Instrumentation at function level
3. Custom span attributes in manaul instrumentation

## Getting Started:

Currently this repo is not available in pypi 
So you can clone the git repository 
and install this package in your project in the following way

```
pip install  /path/to/your/clonedrepo
```

### Set the environment varaibles in you FastAPI app

export SIGNZY_TRACE_SERVICE_NAME=demo-service
export SIGNZY_TRACING_ENDPOINT=http://localhost:4317/api/traces
export SIGNZY_ENABLE_TRACING=true

### Applying AutoInstrumentation for your app

```
from signzy_distributed_tracing_utils import instrument

app = FastAPI()
instrument(app)
```

### Applying Manual Instrumentation

```
from signzy_distributed_tracing_utils import instrument_with_tracing


@instrument_with_tracing()
def dummy_function():
    # your function logic


```

### Setting Custom Attributes

```
from signzy_distributed_tracing_utils import instrument_with_tracing


@instrument_with_tracing(span_attrs={"endpoint": "https://api.sampleapis.com/coffee/hot", "method": "GET"})
def dummy_function():
    # your function logic

```

### You also have the option to setup a custom name for your function (Optional) if not set default function name will be taken
```
from signzy_distributed_tracing_utils import instrument_with_tracing


@instrument_with_tracing(operation_name="my_function)
def dummy_function():
    # your function logic

```


## Todo:

Logger
Automatic env varaible for tracing endpoint based on instrumentation
Instrumentation for Triton
Intrumentation for Postgre
Instrumentation for Falcon
Multiprocessing 
Message Queues
