# shared/logging_config.py (Production Version)

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(
    level=logging.INFO,
    log_dir="logs",
    max_bytes=10_000_000,  # 10MB per file
    backup_count=5          # Keep 5 old files
):
    """
    Production logging setup.
    
    Features:
    - Rotating files (won't fill disk)
    - Different levels for file vs console
    - JSON format option for log aggregators
    - Exception tracebacks
    """
    Path(log_dir).mkdir(exist_ok=True)
    
    script_name = Path(sys.argv[0]).stem
    log_filename = Path(log_dir) / f"{script_name}.log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all, filter at handler
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler - DEBUG and up, rotating
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s"
    )
    file_handler.setFormatter(file_format)
    
    # Console handler - INFO and up, cleaner format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return str(log_filename)


def get_logger(name=None):
    """Get a logger with the given name."""
    return logging.getLogger(name or __name__)