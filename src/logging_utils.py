from __future__ import annotations

from contextlib import contextmanager
import json
import logging
from typing import Iterator


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


@contextmanager
def log_step(logger: logging.Logger, step_name: str) -> Iterator[None]:
    logger.info("STEP START: %s", step_name)
    try:
        yield
    except Exception:
        logger.exception("STEP FAIL: %s", step_name)
        raise
    logger.info("STEP PASS: %s", step_name)


def payload_preview(payload: object, max_chars: int = 500) -> str:
    try:
        text = json.dumps(payload, ensure_ascii=True)
    except TypeError:
        text = str(payload)

    if len(text) > max_chars:
        return text[:max_chars] + "...(truncated)"
    return text
