"""Centralized logging setup for VitaGraph.

The rest of the package calls ``get_logger(__name__)`` instead of using bare
``print()`` calls, so downstream users of the library can control verbosity
and format (or redirect output) the same way they would for any other
Python package.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Returns a configured module-level logger.

    Idempotent: calling this repeatedly for the same ``name`` will not
    attach duplicate handlers (which would otherwise duplicate every log
    line), and it never touches the root logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
