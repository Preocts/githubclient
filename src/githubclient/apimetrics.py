"""
Capture metrics of api requests: elapse (ms) and object size (bytes)

Author: Preocts (Preocts#8196)
"""
import logging
import sys
import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union


logger = logging.getLogger("APIMetrics")


def capmetrics(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tic = time.perf_counter_ns()

        result = func(*args, **kwargs)

        elapse = (time.perf_counter_ns() - tic) / 1_000_000

        logger.debug(
            "func: %s, in: %s bytes, out: %s bytes, elspse: %s ms",
            func.__name__,
            sizeof(args) + sizeof(kwargs),
            sizeof(result),
            round(elapse, 2),
        )

        return result

    return wrapper


def sizeof(obj: Union[Dict[str, Any], List[Any], Tuple[Any, ...]]) -> int:
    """Return total size in bytes of object (included nested)"""
    size_of = 0
    for val in obj.values() if isinstance(obj, dict) else obj:
        nested = isinstance(val, (dict, list, tuple))
        size_of += sizeof(val) if nested else sys.getsizeof(val)
    return size_of
