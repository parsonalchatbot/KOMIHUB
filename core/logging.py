import logging
import logging.handlers
import os
import sys
from pathlib import Path

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

def setup_logging():
    """Setup logging configuration for different environments"""
    
    # Get log level from environment or config
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    log_to_console = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    
    # Convert log level string to logging constant
    level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler with rotation
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "komihub.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Use colored output only if we're in a terminal (not web service)
        if sys.stdout.isatty() and os.getenv("NO_COLOR", "false").lower() != "true":
            from colorama import Fore, Style, init
            init(autoreset=True)
            
            class ColoredFormatter(logging.Formatter):
                def format(self, record):
                    if record.levelno == logging.DEBUG:
                        color = Fore.CYAN
                    elif record.levelno == logging.INFO:
                        color = Fore.GREEN
                    elif record.levelno == logging.WARNING:
                        color = Fore.YELLOW
                    elif record.levelno == logging.ERROR:
                        color = Fore.RED
                    elif record.levelno == logging.CRITICAL:
                        color = Fore.MAGENTA
                    else:
                        color = Fore.WHITE
                    
                    record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                    return super().format(record)
            
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            # Simple formatter for non-terminals (web services)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

# Setup logging on import
setup_logging()

# Get the main logger
logger = logging.getLogger("komihub_bot")

def log_command(command, user):
    logger.info(f"Command '{command}' executed by user {user}")

def log_event(event, details):
    logger.info(f"Event '{event}': {details}")

def log_error(error):
    logger.error(f"Error: {error}")

def log_warning(warning):
    logger.warning(f"Warning: {warning}")

def log_debug(debug):
    logger.debug(f"Debug: {debug}")

def get_log_file_path():
    """Get the path to the main log file"""
    return logs_dir / "komihub.log"

def get_error_log_path():
    """Get the path to the error log file"""
    return logs_dir / "error.log"
