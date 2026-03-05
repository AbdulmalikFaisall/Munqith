"""Logging configuration for Munqith.

Provides structured logging with support for both text and JSON formats.
Called early from app.main to ensure all logs are captured.
"""
import logging
import logging.config
import json
import sys
import os
from pathlib import Path


# Log format styles
TEXT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_FORMAT = "%(message)s"


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def configure_logging():
    """Configure Python logging for Munqith.

    Sets up:
    - Console output (stdout for info+, stderr for errors)
    - Separate loggers for modules
    - JSON or text formatting based on environment
    - Structured logging for monitoring/observability

    Call this function early from app initialization.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()

    # Validate log level
    if log_level not in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]:
        log_level = "INFO"

    # Create logs directory if needed
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(TEXT_FORMAT)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional - only for production)
    if os.getenv("ENV") == "production":
        file_handler = logging.FileHandler("logs/munqith.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configure specific loggers
    # Suppress noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    # App-specific loggers
    logging.getLogger("app").setLevel(log_level)
    logging.getLogger("app.domain").setLevel(log_level)
    logging.getLogger("app.application").setLevel(log_level)
    logging.getLogger("app.infrastructure").setLevel(log_level)
    logging.getLogger("app.api").setLevel(log_level)
    logging.getLogger("app.analytics").setLevel(log_level)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
