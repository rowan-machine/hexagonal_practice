"""
Logging mixin for pipeline components.
"""
import logging
from typing import Optional


class LoggingMixin:
    """Mixin providing logging capabilities to pipeline components."""
    
    def __init__(self, *args, logger_name: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log an info message with optional context."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.info(message)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log a warning message with optional context."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log an error message with optional exception."""
        if error:
            message = f"{message} | Error: {str(error)}"
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.error(message, exc_info=error)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log a debug message with optional context."""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.debug(message)

