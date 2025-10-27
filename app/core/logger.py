import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: Custom log format string (optional)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        
    Returns:
        Configured logger instance
    """
    
    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Default log file path
    if log_file is None:
        log_file = "logs/app.log"
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": [],
                "propagate": False
            },
            "app": {  # Application logger
                "level": log_level,
                "handlers": [],
                "propagate": False
            },
            "uvicorn": {  # Uvicorn logger
                "level": "INFO",
                "handlers": [],
                "propagate": False
            },
            "uvicorn.access": {  # Uvicorn access logger
                "level": "INFO",
                "handlers": [],
                "propagate": False
            },
            "fastapi": {  # FastAPI logger
                "level": "INFO",
                "handlers": [],
                "propagate": False
            }
        }
    }
    
    # Add console handler if enabled
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "default",
            "stream": sys.stdout
        }
        
        # Add console handler to all loggers
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("console")
    
    # Add file handler if enabled
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
        
        # Add file handler to all loggers
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get the main application logger
    logger = logging.getLogger("app")
    
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (defaults to "app")
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully, returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            raise
    
    return wrapper


def log_api_request(request_data: dict, response_data: dict = None, status_code: int = None):
    """
    Log API request and response data.
    
    Args:
        request_data: Request data dictionary
        response_data: Response data dictionary (optional)
        status_code: HTTP status code (optional)
    """
    logger = get_logger("app.api")
    
    log_data = {
        "request": request_data,
        "status_code": status_code
    }
    
    if response_data:
        log_data["response"] = response_data
    
    logger.info(f"API Request/Response: {log_data}")


def log_error(error: Exception, context: str = None):
    """
    Log error with context information.
    
    Args:
        error: Exception instance
        context: Additional context information
    """
    logger = get_logger("app.error")
    
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context
    }
    
    logger.error(f"Error occurred: {error_info}", exc_info=True)


def log_performance(operation: str, duration: float, metadata: dict = None):
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        metadata: Additional metadata
    """
    logger = get_logger("app.performance")
    
    perf_data = {
        "operation": operation,
        "duration": duration,
        "metadata": metadata or {}
    }
    
    logger.info(f"Performance: {perf_data}")


# Initialize default logger
default_logger = setup_logging(
    log_level="DEBUG",
    enable_console=True,
    enable_file=True
)

# Export commonly used loggers
app_logger = get_logger("app")
api_logger = get_logger("app.api")
error_logger = get_logger("app.error")
performance_logger = get_logger("app.performance")
