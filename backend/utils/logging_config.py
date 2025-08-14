"""
Centralized logging configuration for the application
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """
    Configure logging for both development and production
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove default handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # 1. General application log (rotating file)
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_handler)
    
    # 2. Scraping-specific log (rotating file)
    scraping_logger = logging.getLogger('scraping')
    scraping_handler = RotatingFileHandler(
        'logs/scraping.log',
        maxBytes=5*1024*1024,   # 5MB
        backupCount=5
    )
    scraping_handler.setLevel(logging.INFO)
    scraping_handler.setFormatter(simple_formatter)
    scraping_logger.addHandler(scraping_handler)
    scraping_logger.setLevel(logging.INFO)
    scraping_logger.propagate = False  # Don't also log to root logger
    
    # 3. Error-only log (for critical issues)
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,   # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. Console output (for development)
    if app.config.get('ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    app.logger.info("Logging configuration initialized")

def log_job_execution(job_name, success, details=None):
    """
    Helper function to log scheduled job executions
    """
    logger = logging.getLogger('scraping')
    
    status = "SUCCESS" if success else "FAILED"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"[{job_name}] {status} at {timestamp}"
    if details:
        message += f" - {details}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)