"""Utility classes, primarily for logging and data sanitisation."""

import logging
import re


class SensitiveDataFilter(logging.Filter):
    """Redact sensitive values (passwords, tokens, secrets) from log messages.

    Applied via the ``filters`` option on a logging ``Handler`` in
    ``config/settings/base.py``.
    """

    SENSITIVE_PATTERNS: list = [
        (
            re.compile(
                r"(password|token|secret|key)[\"']?\s*[:=]\s*[\"']?([^\"'\\s,]+)", re.I
            ),
            r"\1=***",
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data in the log record's message.

        Args:
            record: The log record to filter.

        Returns:
            Always ``True`` (the record is never suppressed).
        """
        message = record.getMessage()
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        record.msg = message
        return True
