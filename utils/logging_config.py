import logging
import sys
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: f"{grey}%(asctime)s - %(levelname)s - %(message)s{reset}",
        logging.INFO: f"{blue}%(asctime)s - %(levelname)s - %(message)s{reset}",
        logging.WARNING: f"{yellow}%(asctime)s - %(levelname)s - %(message)s{reset}",
        logging.ERROR: f"{red}%(asctime)s - %(levelname)s - %(message)s{reset}",
        logging.CRITICAL: f"{bold_red}%(asctime)s - %(levelname)s - %(message)s{reset}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class JsonFormatter(logging.Formatter):
    """JSON formatter for file logging"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_logging(
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration with both console and file handlers
    
    Args:
        console_level: Logging level for console output
        file_level: Logging level for file output
        log_file: Optional path to log file. If None, logs/app.log will be used
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger("blogging_assistant")
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    
    return logger

def log_separator(logger: logging.Logger, message: str = "", level: int = logging.DEBUG):
    """Log a separator line with optional message"""
    sep_line = "=" * 50
    if message:
        sep_line = f"{sep_line}\n{message}\n{sep_line}"
    logger.log(level, sep_line)

def pretty_print_json(obj: dict, logger: logging.Logger, level: int = logging.DEBUG):
    """Pretty print a JSON object to the log"""
    logger.log(level, json.dumps(obj, indent=2))
