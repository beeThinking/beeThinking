import json
import logging
import time
from collections import Counter

from fastapi import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in ("method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


metrics = Counter()


def configure_logging() -> None:
    logger = logging.getLogger("beethinking.request")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


async def request_metrics(request: Request, call_next) -> Response:
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        metrics["errors_total"] += 1
        raise
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        metrics["requests_total"] += 1
        metrics[f"status_{status_code}_total"] += 1
        metrics["request_duration_ms_total"] += duration_ms
        logging.getLogger("beethinking.request").info(
            "request_complete",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
