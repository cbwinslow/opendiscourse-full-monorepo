"""OpenDiscourse - A platform for analyzing government documents and legislative data.

This package provides tools for processing, analyzing, and searching through
government documents and legislative data.
"""

__version__ = "0.1.0"

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Import core functionality
from .core.config import settings  # noqa: E402

__all__ = ["settings"]
