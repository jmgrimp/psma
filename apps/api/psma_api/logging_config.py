from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from psma_api.logging_context import request_id_var


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": getattr(record, "service", None) or os.getenv("PSMA_SERVICE", "psma-api"),
            "env": getattr(record, "env", None) or os.getenv("PSMA_ENV", "local"),
            "version": getattr(record, "version", None) or os.getenv("PSMA_VERSION", "0.0.0"),
        }

        # Common structured extras (we keep them flat and optional)
        for key in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "upstream",
            "url",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        ts = datetime.now(timezone.utc).isoformat()
        rid = getattr(record, "request_id", None)
        base = f"{ts} {record.levelname} {record.name} {record.getMessage()}"
        if rid:
            base += f" request_id={rid}"
        if getattr(record, "status_code", None) is not None:
            base += f" status={getattr(record, 'status_code')}"
        if getattr(record, "duration_ms", None) is not None:
            base += f" duration_ms={getattr(record, 'duration_ms')}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        # Make request_id available on every log record without needing to pass it.
        rid = getattr(record, "request_id", None) or request_id_var.get()
        record.request_id = rid
        return True


def setup_logging(*, level: str = "INFO", fmt: str = "json") -> None:
    """Configure app logging.

    - Uses stdout
    - Supports json or text format
    - Keeps uvicorn loggers consistent
    """

    env = os.getenv("PSMA_ENV", "local").lower()

    # If the user explicitly sets PSMA_LOG_LEVEL/FORMAT, honor them.
    # Otherwise choose sensible defaults based on environment.
    resolved_level = os.getenv("PSMA_LOG_LEVEL")
    resolved_format = os.getenv("PSMA_LOG_FORMAT")
    if resolved_level is None:
        resolved_level = ("DEBUG" if env in {"local", "dev", "development"} else level).upper()
    else:
        resolved_level = resolved_level.upper()

    if resolved_format is None:
        resolved_format = ("text" if env in {"local", "dev", "development"} else fmt).lower()
    else:
        resolved_format = resolved_format.lower()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    if resolved_format == "text":
        handler.setFormatter(TextFormatter())
    else:
        handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(resolved_level)

    # Align common server loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    # Access logs are useful in dev, but can be noisy in prod.
    access_enabled = os.getenv("PSMA_LOG_UVICORN_ACCESS")
    if access_enabled is None:
        access_enabled = "1" if env in {"local", "dev", "development"} else "0"
    if access_enabled.strip() in {"0", "false", "False", "no", "NO"}:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
