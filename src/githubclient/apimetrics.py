"""
Capture metrics of api requests: elapse (ms) and object size (bytes)

Author: Preocts (Preocts#8196)
"""
from __future__ import annotations

import logging
import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger("APIMetrics")


def capmetrics(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        now = time.time()

        tic = time.perf_counter_ns()

        result = func(*args, **kwargs)

        elapse = (time.perf_counter_ns() - tic) / 1_000_000

        logger.debug(
            "epoch: %s, func: %s, in: %s bytes, out: %s bytes, elspse: %s ms",
            now,
            func.__name__,
            sizeof(args) + sizeof(kwargs),
            sizeof(result),
            round(elapse, 2),
        )

        return result

    return wrapper


def sizeof(obj: dict[str, Any] | list[Any] | tuple[Any, ...]) -> int:
    """Return total size in bytes of object (included nested)"""
    size_of = 0
    for val in obj.values() if isinstance(obj, dict) else obj:
        nested = isinstance(val, (dict, list, tuple))
        size_of += sizeof(val) if nested else sys.getsizeof(val)
    return size_of
