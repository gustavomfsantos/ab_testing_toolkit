"""Centralized logging configuration for the toolkit."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger for a project module.

    Centralized logging matters in a data pipeline because consistent timestamps,
    levels, and module names make a statistical workflow auditable and easier to
    debug when results are reproduced later.

    Args:
        name: Name to attach to log records, usually ``__name__``.

    Returns:
        A configured logger that writes informative messages to stderr.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
