"""Structured logging.

Every Bedrock call must log latency, token usage and model ID (rules/ai.md).
That is enforced BY CONSTRUCTION in `ai_clients/bedrock_client.py` — a caller
cannot forget, because the wrapper does it.

Why it matters: it is the only defence against the two failure modes that cost
real money. Silent AI degradation shows up as rising latency/fallback long
before a customer complains, and runaway Bedrock spend shows up as token counts
before it shows up as an invoice (22-risk-register.md §2, §3).
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    """One JSON object per line. CloudWatch and every log tool can parse it."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Anything passed via `extra=` rides along.
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__ and key not in (
                "message",
                "asctime",
            ):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Call once, from main.py."""
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
